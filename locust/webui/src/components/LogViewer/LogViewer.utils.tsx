export const isImportantLog = (log: string) =>
  log.includes('WARNING') || log.includes('ERROR') || log.includes('CRITICAL');
