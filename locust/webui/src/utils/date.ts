export const formatLocaleString = (utcTimestamp: string) =>
  utcTimestamp ? new Date(utcTimestamp).toLocaleString() : '';

export const formatLocaleTime = (utcTimestamp: string) =>
  utcTimestamp ? new Date(utcTimestamp).toLocaleTimeString() : '';
