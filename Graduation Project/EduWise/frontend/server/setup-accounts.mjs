import { setupAccounts } from './accounts.mjs';

try {
  const credentials = await setupAccounts();
  console.log('Save these generated local credentials. Only password hashes are stored.');
  console.table(credentials.map(({ email, password }) => ({ email, password })));
} catch (error) {
  if (error.code === 'EEXIST') console.error('Accounts already exist. The existing credentials were preserved.');
  else console.error(error);
  process.exitCode = 1;
}
