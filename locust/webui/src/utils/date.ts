export const formatLocaleString = (utcTimestamp: string) => new Date(utcTimestamp).toLocaleString();

export const formatLocaleTime = (utcTimestamp: string) =>
  new Date(utcTimestamp).toLocaleTimeString();
