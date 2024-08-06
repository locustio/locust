const isDate = (timestamp: string) => !isNaN(Date.parse(timestamp));

export const formatLocaleString = (utcTimestamp: string) =>
  utcTimestamp && isDate(utcTimestamp) ? new Date(utcTimestamp).toLocaleString() : '';

export const formatLocaleTime = (utcTimestamp: string) =>
  utcTimestamp && isDate(utcTimestamp) ? new Date(utcTimestamp).toLocaleTimeString() : '';
