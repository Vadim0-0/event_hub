const AUTH_PUBLIC_PATHS = ['/auth/login', '/auth/register'];

function isAuthPublicPath(url: string) {
  return AUTH_PUBLIC_PATHS.some((publicPath) => url.includes(publicPath))
};

function getRequestUrl(request: RequestInfo) {
  return typeof request === 'string' ? request : request.toString()
};

export const useApi = () => {
  const config = useRuntimeConfig();

  const api = $fetch.create({
    baseURL: config.public.apiBase as string,

    onRequest({ options, request }) {
      const url = getRequestUrl(request)
      const token = useCookie<string | null>('auth_token')

      if (token.value && !isAuthPublicPath(url)) {
        const headers = new Headers(options.headers as HeadersInit)
        headers.set('Authorization', `Bearer ${token.value}`)
        options.headers = headers
      }
    },

    onResponseError({ response, request }) {
      const url = getRequestUrl(request)
      const token = useCookie<string | null>('auth_token')

      if (response.status === 401 && token.value && !isAuthPublicPath(url)) {
        token.value = null
        navigateTo('/auth')
      }
    },
  });

  return api
};