import { randomBytes, scrypt, timingSafeEqual } from 'node:crypto';
import { mkdir, writeFile } from 'node:fs/promises';
import { isAbsolute, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';

export const dataDir = process.env.EDUFLOW_DATA_DIR || fileURLToPath(new URL('./.data/', import.meta.url));
if (!isAbsolute(dataDir)) throw new Error('EDUFLOW_DATA_DIR must be an absolute path.');
export const accountFile = join(dataDir, 'accounts.json');

const derive = promisify(scrypt);
const keyLength = 64;
const unknownAccount = { salt: '0'.repeat(32), hash: '0'.repeat(keyLength * 2) };
const roles = ['admin', 'teacher', 'secretary'];

export async function setupAccounts(directory = dataDir) {
  const credentials = roles.map(role => ({
    id: `user-${role}`,
    email: `${role}@eduflow.test`,
    password: randomBytes(18).toString('base64url'),
  }));
  const accounts = await Promise.all(credentials.map(async ({ id, email, password }) => {
    const salt = randomBytes(16).toString('hex');
    const hash = await derive(password, salt, keyLength);
    return { id, email, salt, hash: hash.toString('hex') };
  }));
  await mkdir(directory, { recursive: true, mode: 0o700 });
  await writeFile(join(directory, 'accounts.json'), JSON.stringify(accounts, null, 2), { flag: 'wx', mode: 0o600 });
  return credentials;
}

export async function verifyAccount(accounts, email, password) {
  const account = accounts.find(entry => entry.email === email.trim().toLowerCase());
  const { salt, hash } = account ?? unknownAccount;
  const key = await derive(password, salt, keyLength);
  return timingSafeEqual(key, Buffer.from(hash, 'hex')) ? account : undefined;
}
