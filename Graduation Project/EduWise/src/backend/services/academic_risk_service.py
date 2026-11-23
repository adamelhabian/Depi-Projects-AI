"""Importable FastAPI service boundary for single-student evaluation, explainability, and simulation."""

from pathlib import Path

import pandas as pd
import xgboost as xgb
from pydantic import ValidationError

from src.config.settings import MODEL_PATH
from src.machine_learning.models.academic_risk_model import AcademicRiskModel
from src.machine_learning.preprocessing.academic_risk_preprocessor import StudentSnapshot

FACTOR_DESCRIPTIONS = {
    "quiz_latest": {
        "label_ar": "درجة آخر كويز",
        "label_en": "Latest Quiz Score",
        "advice_ar": "تقديم حصة مراجعة سريعة للمفاهيم التي وردت في آخر كويز.",
        "advice_en": "Provide a quick review session covering concepts from the latest quiz.",
    },
    "quiz_middle": {
        "label_ar": "درجة كويز منتصف الفترة",
        "label_en": "Mid-period Quiz Score",
        "advice_ar": "مراجعة كشكول الملاحظات وحل أسئلة تطبيقية مشابهة.",
        "advice_en": "Review notes and practice similar sample questions.",
    },
    "quiz_oldest": {
        "label_ar": "درجة أول كويز",
        "label_en": "Initial Quiz Score",
        "advice_ar": "تثبيت الأساسيات والمفاهيم الأولية للمنهج.",
        "advice_en": "Reinforce foundational course principles.",
    },
    "quiz_trend": {
        "label_ar": "منحنى تطور/تراجع الكويزات",
        "label_en": "Quiz Score Trend",
        "advice_ar": "ملاحظة التراجع التدريجي في الدرجات وعقد جلسة تقييم فردية.",
        "advice_en": "Note continuous score drop and conduct an individual check-in.",
    },
    "attendance_rate": {
        "label_ar": "نسبة الحضور الإجمالية",
        "label_en": "Overall Attendance Rate",
        "advice_ar": "ضرورة التزام الطالب بالحضور وعدم تكرار الغياب بدون عذر مقبول.",
        "advice_en": "Ensure consistent attendance and follow up on unexcused absences.",
    },
    "homework_completion_rate": {
        "label_ar": "نسبة تسليم الواجبات",
        "label_en": "Homework Completion Rate",
        "advice_ar": "متابعة كراسة الواجب وإلزام الطالب بتسليم التكليفات في مواعيدها.",
        "advice_en": "Follow up on assignments and set strict submission deadlines.",
    },
    "average_quiz_score": {
        "label_ar": "متوسط درجات الكويزات",
        "label_en": "Average Quiz Score",
        "advice_ar": "تكثيف حل التدريبات العملية لرفع المتوسط العام.",
        "advice_en": "Intensify practical exercises to raise general quiz average.",
    },
    "midterm_score": {
        "label_ar": "درجة امتحان نصف الفصل",
        "label_en": "Midterm Exam Score",
        "advice_ar": "مراجعة شاملة لأسئلة الامتحان النصفي والتركيز على نقاط الضعف.",
        "advice_en": "Conduct a full exam recap focusing on identified weaknesses.",
    },
    "participation_score": {
        "label_ar": "درجة التفاعل والمشاركة",
        "label_en": "Classroom Participation",
        "advice_ar": "تحفيز الطالب على المشاركة الصفية وطرح الأسئلة أثناء الشرح.",
        "advice_en": "Encourage active class participation and questioning during lectures.",
    },
    "missed_sessions_count": {
        "label_ar": "عدد الحصص الغائبة",
        "label_en": "Missed Sessions Count",
        "advice_ar": "جدولة جلسة تعويضية للمحتوى الذي فات الطالب أثناء غيابه.",
        "advice_en": "Schedule a makeup session for topics missed during absences.",
    },
}


class InvalidStudentData(ValueError):
    """The caller supplied invalid measurements or no usable evidence."""


class AcademicRiskService:
    """Load a trusted artifact once per application worker."""

    def __init__(self, model_path: Path = MODEL_PATH) -> None:
        self.model = AcademicRiskModel.load(model_path)

    def _validate_student(self, student_data: dict) -> StudentSnapshot:
        try:
            return StudentSnapshot.model_validate(student_data)
        except ValidationError as exc:
            raise InvalidStudentData(str(exc.errors(include_input=False, include_context=False))) from exc

    def predict(self, student_data: dict, include_explanation: bool = False) -> dict:
        """Return a JSON-safe prediction using the training-time decision threshold."""
        student = self._validate_student(student_data)
        probability = float(self.model.probabilities(pd.DataFrame([student.model_dump()]))[0])
        result = {
            "student_id": student.student_id, "group_id": student.group_id,
            "risk_probability": probability, "risk_threshold": self.model.threshold,
            "is_at_risk": int(probability >= self.model.threshold), "model_version": self.model.model_version,
        }
        if include_explanation:
            result["explanation"] = self.explain(student_data)
        return result

    def explain(self, student_data: dict) -> dict:
        """Explain model prediction using native TreeSHAP feature attributions."""
        student = self._validate_student(student_data)
        df = pd.DataFrame([student.model_dump()])

        preprocessor = self.model.pipeline.named_steps["preprocess"]
        clf = self.model.pipeline.named_steps["classifier"]

        X_trans = preprocessor.transform(df)
        feature_names = preprocessor.named_steps["columns"].get_feature_names_out()

        probability = float(self.model.probabilities(df)[0])
        is_at_risk = int(probability >= self.model.threshold)

        # TreeSHAP computation
        booster = clf.get_booster()
        dmatrix = xgb.DMatrix(X_trans, feature_names=list(feature_names))
        contribs = booster.predict(dmatrix, pred_contribs=True)
        shap_values = contribs[0, :-1]

        # Aggregate contributions by clean feature key
        aggregated: dict[str, float] = {}
        for raw_name, val in zip(feature_names, shap_values):
            clean = raw_name.replace("numeric__", "").replace("group__", "")
            # If indicator column e.g. missingvalue indicator, attach to main feature
            base_key = clean.replace("missingvalue_", "")
            aggregated[base_key] = aggregated.get(base_key, 0.0) + float(val)

        # Risk factors (positive shap) vs Protective factors (negative shap)
        risk_factors = []
        protective_factors = []
        action_recommendations_ar = []
        action_recommendations_en = []

        for key, val in aggregated.items():
            meta = FACTOR_DESCRIPTIONS.get(key)
            if not meta or abs(val) < 0.02:
                continue

            entry = {
                "feature": key,
                "label_ar": meta["label_ar"],
                "label_en": meta["label_en"],
                "impact": round(val, 3),
            }

            if val > 0:
                risk_factors.append(entry)
                action_recommendations_ar.append(meta["advice_ar"])
                action_recommendations_en.append(meta["advice_en"])
            else:
                protective_factors.append(entry)

        risk_factors.sort(key=lambda x: x["impact"], reverse=True)
        protective_factors.sort(key=lambda x: x["impact"])

        # Determine qualitative category
        if probability < 0.30:
            category_ar, category_en = "مستقر / آمن", "Safe / Stable"
        elif probability < self.model.threshold:
            category_ar, category_en = "متوسط / تحت الملاحظة", "Moderate / Watchlist"
        else:
            category_ar, category_en = "مرتفع / معرض للتعثر", "High / Academic Risk"

        return {
            "student_id": student.student_id,
            "risk_probability": round(probability, 4),
            "threshold": self.model.threshold,
            "is_at_risk": is_at_risk,
            "risk_category": {"ar": category_ar, "en": category_en},
            "top_risk_factors": risk_factors[:3],
            "top_protective_factors": protective_factors[:3],
            "recommended_actions": {
                "ar": action_recommendations_ar[:2] or ["الاستمرار في المتابعة الدورية للطالب."],
                "en": action_recommendations_en[:2] or ["Continue regular periodic student tracking."],
            },
        }

    def simulate_what_if(self, student_data: dict, improvements: dict) -> dict:
        """Simulate the impact of proposed academic improvements on student risk."""
        base_student = self._validate_student(student_data)
        base_prob = float(self.model.probabilities(pd.DataFrame([base_student.model_dump()]))[0])

        simulated_data = dict(student_data)
        for key, val in improvements.items():
            if hasattr(base_student, key):
                simulated_data[key] = val

        sim_student = self._validate_student(simulated_data)
        sim_prob = float(self.model.probabilities(pd.DataFrame([sim_student.model_dump()]))[0])

        delta = round(base_prob - sim_prob, 4)
        return {
            "student_id": base_student.student_id,
            "baseline_probability": round(base_prob, 4),
            "simulated_probability": round(sim_prob, 4),
            "risk_reduction": max(0.0, delta),
            "baseline_is_at_risk": int(base_prob >= self.model.threshold),
            "simulated_is_at_risk": int(sim_prob >= self.model.threshold),
            "rescued_from_risk": bool(base_prob >= self.model.threshold and sim_prob < self.model.threshold),
        }

