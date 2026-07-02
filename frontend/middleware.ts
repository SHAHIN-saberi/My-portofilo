import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Protect all /adshs/* routes except /adshs/login
  if (pathname.startsWith('/adshs') && pathname !== '/adshs/login') {
    const adminToken = request.cookies.get('admin_token')
    
    if (!adminToken) {
      // No auth cookie, redirect to login
      const loginUrl = new URL('/adshs/login', request.url)
      loginUrl.searchParams.set('redirect', pathname)
      return NextResponse.redirect(loginUrl)
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: '/adshs/:path*',
}
