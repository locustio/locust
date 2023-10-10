import { queryStringToObject } from 'utils/string';

export const pushQuery = (query: { [key: string]: string }) => {
  const url = new URL(window.location.href);

  for (const [key, value] of Object.entries(query)) {
    url.searchParams.set(key, value);
  }

  window.history.pushState(null, '', url);
};

export const getUrlParams = (): { [key: string]: string } | null =>
  window.location.search ? queryStringToObject(window.location.search) : null;
