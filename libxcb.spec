%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%define xpyb_version 1.1

# Define this when bootstrapping to avoid the xpyb loop
#define bootstrap 1

Name:           libxcb
Version:        1.5
Release:        1%{?dist}
Summary:        A C binding to the X11 protocol

Group:          System Environment/Libraries
License:        MIT
URL:            http://xcb.freedesktop.org/
Source0:        http://xcb.freedesktop.org/dist/%{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
# This is stolen straight from the pthread-stubs source:
# http://cgit.freedesktop.org/xcb/pthread-stubs/blob/?id=6900598192bacf5fd9a34619b11328f746a5956d
# we don't need the library because glibc has working pthreads, but we need
# the pkgconfig file so libs that link against libxcb know this...
Source1:	pthread-stubs.pc.in
Source2:	http://xcb.freedesktop.org/dist/xpyb-%{xpyb_version}.tar.bz2 


BuildRequires:  autoconf automake libtool pkgconfig
BuildRequires:  doxygen
BuildRequires:  graphviz
BuildRequires:  libXau-devel
BuildRequires:  libxslt
BuildRequires:	python-devel
BuildRequires:  xcb-proto >= 1.6
BuildRequires:  xorg-x11-proto-devel
BuildRequires:  xorg-x11-util-macros
%if !0%{?bootstrap}
BuildRequires:	libxcb-devel
%endif

%description
The X protocol C-language Binding (XCB) is a replacement for Xlib featuring a
small footprint, latency hiding, direct access to the protocol, improved
threading support, and extensibility.

%package        devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       pkgconfig

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package        doc
Summary:        Documentation for %{name}
Group:          Documentation
BuildArch:	noarch

%description    doc
The %{name}-doc package contains documentation for the %{name} library.

%if !0%{?bootstrap}
%package	python
Summary:	Python bindings for %{name}
Group:		Development/Libraries
Provides:	xpyb

%description	python
Python bindings for %{name}.
%endif

%prep
%setup -q -b2

%if !0%{?bootstrap}
pushd ../xpyb-%{xpyb_version}
# XXX fix me upstream please
sed -i 's@$(pythondir)@$(pyexecdir)@' src/Makefile.am
popd
%endif

%build
autoreconf -v --install
%configure --disable-static --docdir=%{_datadir}/doc/%{name}-%{version} \
	   --enable-selinux
make %{?_smp_mflags}

%if !0%{?bootstrap}
pushd ../xpyb-%{xpyb_version}
autoreconf -v --install
%configure
make %{?_smp_mflags}
popd
%endif

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
rm -f $RPM_BUILD_ROOT/%{_libdir}/libxcb-xprint.so*
rm -f $RPM_BUILD_ROOT/%{_includedir}/xcb/xprint.h
install -m 644 COPYING NEWS README $RPM_BUILD_ROOT/%{_datadir}/doc/%{name}-%{version}
sed 's,@libdir@,%{_libdir},;s,@prefix@,%{_prefix},;s,@exec_prefix@,%{_exec_prefix},' %{SOURCE1} > $RPM_BUILD_ROOT%{_libdir}/pkgconfig/pthread-stubs.pc

%if !0%{?bootstrap}
pushd ../xpyb-%{xpyb_version}
make install DESTDIR=$RPM_BUILD_ROOT
popd
%endif

find $RPM_BUILD_ROOT -name '*.la' -delete

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%{_libdir}/libxcb-composite.so.0*
%{_libdir}/libxcb-damage.so.0*
%{_libdir}/libxcb-dpms.so.0*
%{_libdir}/libxcb-dri2.so.0*
%{_libdir}/libxcb-glx.so.0*
%{_libdir}/libxcb-randr.so.0*
%{_libdir}/libxcb-record.so.0*
%{_libdir}/libxcb-render.so.0*
%{_libdir}/libxcb-res.so.0*
%{_libdir}/libxcb-screensaver.so.0*
%{_libdir}/libxcb-shape.so.0*
%{_libdir}/libxcb-shm.so.0*
%{_libdir}/libxcb-sync.so.0*
%{_libdir}/libxcb-xevie.so.0*
%{_libdir}/libxcb-xf86dri.so.0*
%{_libdir}/libxcb-xfixes.so.0*
%{_libdir}/libxcb-xinerama.so.0*
%{_libdir}/libxcb-xselinux.so.0*
%{_libdir}/libxcb-xtest.so.0*
%{_libdir}/libxcb-xv.so.0*
%{_libdir}/libxcb-xvmc.so.0*
%{_libdir}/libxcb.so.1*

%files devel
%defattr(-,root,root,-)
%{_includedir}/xcb
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc

%files doc
%defattr(-,root,root,-)
%{_datadir}/doc/%{name}-%{version}

%if !0%{?bootstrap}
%files python
%defattr(-,root,root,-)
%{python_sitearch}/xcb
%endif

%changelog
* Wed Jan 13 2010 Dave Airlie <airlied@redhat.com> 1.5-1
- libxcb 1.5

* Wed Dec 02 2009 Adam Jackson <ajax@redhat.com> 1.4-2
- libxcb-1.4-keepalive.patch: setsockopt(SO_KEEPALIVE) for TCP (#476415)

* Thu Aug 27 2009 Adam Jackson <ajax@redhat.com> 1.4-1
- libxcb 1.4 (#518597)

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul 14 2009 Adam Jackson <ajax@redhat.com> 1.3-1
- libxcb 1.3
- List DSO versions explicitly.
- Don't package any xprint bits.  Seriously, no.

* Mon Jul 13 2009 Adam Jackson <ajax@redhat.com> 1.2-8
- Really fix xpyb build.

* Mon Jul 06 2009 Adam Jackson <ajax@redhat.com> 1.2-7
- Fix xpyb build

* Mon Jun 29 2009 Adam Jackson <ajax@redhat.com> 1.2-6
- BuildRequires: xcb-proto >= 1.5

* Wed Jun 24 2009 Adam Jackson <ajax@redhat.com> 1.2-5
- libxcb-1.2-no-nagle.patch: Disable Nagle's algorithm on TCP. (#442158)

* Tue May 19 2009 Adam Jackson <ajax@redhat.com> 1.2-4
- Add libxcb-python subpackage

* Tue Apr 07 2009 Adam Jackson <ajax@redhat.com> 1.2-3
- libxcb-1.2-to-git-6e2e87d.patch: Various updates from git, XID generation
  being the most important.

* Tue Feb 24 2009 Matthias Clasen <mclasen@redhat.com> 1.2-2
- Make -doc noarch

* Wed Feb 18 2009 Adam Jackson <ajax@redhat.com> 1.2-1
- libxcb 1.2

* Tue Feb 10 2009 Adam Jackson <ajax@redhat.com> 1.1.93-4
- Fix selinux module build. (#474249)

* Sun Feb 08 2009 Adam Jackson <ajax@redhat.com> 1.1.93-3
- Remove aforementioned egregious hack.  Now I can sleep easier.

* Thu Dec 18 2008 Adam Jackson <ajax@redhat.com> 1.1.93-2
- Egregious hack to make the next libX11 build work.  Hands... won't come
  clean...

* Wed Dec 17 2008 Adam Jackson <ajax@redhat.com> 1.1.93-1
- libxcb 1.1.93

* Sun Oct 19 2008 Adam Jackson <ajax@redhat.com> 1.1.91-5
- Add pthread-stubs.pc

* Mon Oct 13 2008 Adam Jackson <ajax@redhat.com> 1.1.91-4
- libxcb-1.1-abstract-socket.patch: Drop.
- libxcb-1.1.91-git.patch: Update to git master.

* Wed Sep 17 2008 Adam Jackson <ajax@redhat.com> 1.1.91-3
- libxcb-1.1-xreply-leak.patch: Plug a memory leak in _XReply when the
  caller has a non-fatal error handler. (mclasen, fdo #17616)

* Thu Sep 11 2008 Adam Jackson <ajax@redhat.com> 1.1.91-2
- Enable x-selinux bindings.

* Wed Sep 10 2008 Adam Jackson <ajax@redhat.com> 1.1.91-1
- libxcb 1.1.91

* Tue Apr 22 2008 Adam Jackson <ajax@redhat.com> 1.1-4
- libxcb-1.1-sloppy-lock.patch: Turn sloppy locking on all the time.  I'm
  tired of fighting it. (#390261)

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.1-2
- Autorebuild for GCC 4.3

* Mon Nov 12 2007 Adam Jackson <ajax@redhat.com> 1.1-1
- libxcb 1.1

* Fri Aug 24 2007 Adam Jackson <ajax@redhat.com> 1.0-3
- libxcb-1.0-abstract-socket.patch: When connecting to the X server, prefer
  abstract-namespace unix sockets to filesystem-bound sockets.

* Wed Aug 22 2007 Adam Jackson <ajax@redhat.com> - 1.0-2
- Rebuild for PPC toolchain bug

* Fri Jun 29 2007 Adam Jackson <ajax@redhat.com> 1.0-1
- Initial revision.
