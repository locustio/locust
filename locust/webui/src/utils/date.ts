const isDate = (timestamp: string) => !isNaN(new Date(timestamp).getTime());

export const formatLocaleString = (utcTimestamp: string) =>
  utcTimestamp && isDate(utcTimestamp) ? new Date(utcTimestamp).toLocaleString() : '';
