const AUTH_PUBLIC_PATHS = ['/auth/login', '/auth/register']

function isAuthPublicPath(url: string) {
  return AUTH_PUBLIC_PATHS.some((publicPath) => url.includes(publicPath))
}

function getRequestUrl(request: RequestInfo) {
  return typeof request === 'string' ? request : request.toString()
}

export const useApi = () => {
  const config = useRuntimeConfig();
  const token = useCookie<string | null>('auth_token');

  const api = $fetch.create({
    baseURL: config.public.apiBase as string,

    onRequest({ options, request }) {
      const url = getRequestUrl(request)
      if (token.value && !isAuthPublicPath(url)) {
        options.headers.set('Authorization', `Bearer ${token.value}`)
      }
    },

    onResponseError({ response, request }) {
      const url = getRequestUrl(request)
      if (response.status === 401 && token.value && !isAuthPublicPath(url)) {
        token.value = null
        navigateTo('/auth')
      }
    },
  });

  return api
};