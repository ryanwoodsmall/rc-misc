%define spname rc

%define editlinever 1.15.3
%define editlinedir editline-%{editlinever}

%define debug_package %{nil}

%if 0%{?fedora} < 17 && 0%{?rhel} < 7
%global _bindir   /bin
%endif

Summary:          Re-implementation for Unix of the Plan 9 shell
Name:             %{spname}-static
Version:          1.7.4
Release:          1%{?dist}
License:          zlib
Group:            System Environment/Shells
URL:              http://tobold.org/article/rc
Source0:          http://static.tobold.org/%{spname}/%{spname}-%{version}.tar.gz
%if 0%{?fedora} >= 17 || 0%{?rhel} >= 7
Conflicts:        filesystem < 3
Provides:         /bin/%{spname}
%endif
Requires(post):   grep
Requires(postun): sed
BuildRequires:    readline-devel
BuildRoot:        %{_tmppath}/%{spname}-%{version}-%{release}-root-%(%{__id_u} -n)

# customizations for static build
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	musl-static
Source1:	https://github.com/troglobit/editline/releases/download/%{editlinever}/editline-%{editlinever}.tar.xz
Patch0:		rc-static-editline.patch
Provides:	%{name}
Provides:	%{spname}

%description
Rc is a command interpreter for Plan 9 that provides similar facilities to
UNIX's Bourne shell, with some small additions and less idiosyncratic syntax.
This is a re-implementation for Unix, by Byron Rakitzis, of the Plan 9 shell.

%prep
%setup -q -n %{spname}-%{version}
%patch0 -p1
autoreconf -fiv .

%build
tar -Jxf %{SOURCE1}
cd %{editlinedir}
./configure \
  --prefix=${PWD}-built \
  --enable-static=yes \
  --enable-static \
  --disable-shared \
  --enable-shared=no \
  CC="musl-gcc" CFLAGS="-Wl,-static" LDFLAGS="-static --static"
make %{?_smp_mflags}
make install
cd ..
%configure \
  --with-edit=editline \
  CC="musl-gcc" CFLAGS="-Wl,-static" LDFLAGS="-static --static -L%{editlinedir}-built/lib" CPPFLAGS="-I%{editlinedir}/include"
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT INSTALL='install -p' install

%check
make check

%post
%if 0%{?fedora} >= 17 || 0%{?rhel} >= 7
grep -q "^/bin/%{spname}$" %{_sysconfdir}/shells 2>/dev/null || \
  echo "/bin/%{spname}" >> %{_sysconfdir}/shells
%endif
grep -q "^%{_bindir}/%{spname}$" %{_sysconfdir}/shells 2>/dev/null || \
  echo "%{_bindir}/%{spname}" >> %{_sysconfdir}/shells

%postun
if [ ! -x %{_bindir}/%{spname} ]; then
%if 0%{?fedora} >= 17 || 0%{?rhel} >= 7
  sed -e 's@^/bin/%{spname}$@POSTUNREMOVE@' -e '/^POSTUNREMOVE$/d' -i %{_sysconfdir}/shells
%endif
  sed -e 's@^%{_bindir}/%{spname}$@POSTUNREMOVE@' -e '/^POSTUNREMOVE$/d' -i %{_sysconfdir}/shells
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license COPYING
%doc ChangeLog AUTHORS EXAMPLES NEWS README
%{_bindir}/%{spname}
%{_mandir}/man1/%{spname}.1*

%changelog
* Fri Feb  9 2018 ryan woodsmall <rwoodsmall@gmail.com> 
- static build with musl and including editline

* Wed May 13 2015 Robert Scheck <robert@fedoraproject.org> 1.7.4-1
- Upgrade to 1.7.4

* Sat May 09 2015 Robert Scheck <robert@fedoraproject.org> 1.7.3-1
- Upgrade to 1.7.3

* Wed Apr 08 2015 Robert Scheck <robert@fedoraproject.org> 1.7.2-1
- Upgrade to 1.7.2
- Initial spec file for Fedora and Red Hat Enterprise Linux
