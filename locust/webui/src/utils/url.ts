import { objectToQueryString, queryStringToObject } from 'utils/string';

export const pushQuery = (query: { [key: string]: string }) => {
  const currentUrl = new URL(window.location.href);

  const newUrl = `${currentUrl.origin}${currentUrl.pathname}${objectToQueryString(query, {
    shouldTransformKeys: false,
  })}`;

  window.history.pushState({ path: newUrl }, '', newUrl);
};

export const getUrlParams = (): { [key: string]: string } | null =>
  window.location.search ? queryStringToObject(window.location.search) : null;
