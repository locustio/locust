import { createFormData } from 'utils/object';
import { camelCaseKeys, snakeCaseKeys, objectToQueryString } from 'utils/string';

export const REQUEST_METHODS = {
  GET: 'GET',
  POST: 'POST',
  PUT: 'PUT',
  DELETE: 'DELETE',
};

interface IGetRequestBody {
  body?: { [key: string]: any } | null;
  form?: boolean;
}

interface ICreateRequestHeaders extends IGetRequestBody {
  method?: string;
}

export interface IAsyncRequestOptions extends ICreateRequestHeaders {
  query?: { [key: string]: string } | null;
}

const getRequestBody = ({ body, form }: IGetRequestBody) => {
  if (!body) {
    return null;
  }

  return form ? createFormData(snakeCaseKeys(body)) : JSON.stringify(snakeCaseKeys(body));
};

const createRequestHeaders = ({ method, body, form }: ICreateRequestHeaders) => ({
  headers: {
    'Content-Type': form ? 'application/x-www-form-urlencoded' : 'application/json',
  },
  method: method,
  body: getRequestBody({ body, form }),
});

interface IBaseResponse {
  statusCode: number;
  message: string;
}

export async function asyncRequest<IResponse>(
  request: string,
  {
    method = REQUEST_METHODS.GET,
    body = null,
    query = null,
    form = false,
  }: IAsyncRequestOptions = {},
) {
  try {
    const queryString = objectToQueryString(query);
    const requestHeaders = createRequestHeaders({ method, body, form });
    const response = await fetch(`${request}${queryString}`, requestHeaders);
    const parsedResponse = camelCaseKeys<IResponse & IBaseResponse>(await response.json());

    if (parsedResponse.statusCode >= 400) {
      throw new Error(
        `Network Error: Status ${parsedResponse.statusCode} ${parsedResponse.message}`,
      );
    }

    return parsedResponse;
  } catch (e) {
    // eslint-disable-next-line no-console
    console.error('Network Error:', e);
    return e;
  }
}
