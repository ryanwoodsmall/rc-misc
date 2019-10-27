%define spname rc

%define editlinever 1.16.0
%define editlinedir editline-%{editlinever}

%define debug_package %{nil}

%if 0%{?fedora} < 17 && 0%{?rhel} < 7
%global _bindir   /bin
%endif

Summary:          Re-implementation for Unix of the Plan 9 shell
Name:             %{spname}-static
Version:          1.7.4
Release:          9%{?dist}
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
BuildRequires:	musl-static >= 1.1.24
Source1:	https://github.com/troglobit/editline/releases/download/%{editlinever}/editline-%{editlinever}.tar.xz
Patch0:		https://raw.githubusercontent.com/ryanwoodsmall/rc-misc/master/rpm/SOURCES/rc-static-editline.patch
#Conflicts:	%{spname}
#Obsoletes:	%{spname}
Provides:	%{name}
Provides:	%{spname}

%description
Rc is a command interpreter for Plan 9 that provides similar facilities to
UNIX's Bourne shell, with some small additions and less idiosyncratic syntax.
This is a re-implementation for Unix, by Byron Rakitzis, of the Plan 9 shell.

%prep
%setup -q -n %{spname}-%{version}
tar -Jxf %{SOURCE1}
%patch0 -p1
autoreconf -fiv .

%build
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
* Sat Oct 26 2019 ryan woodsmall <rwoodsmall@gmail.com>
- release bump for musl 1.1.24

* Wed Jul 17 2019 ryan woodsmall <rwoodsmall@gmail.com>
- release bump for musl 1.1.23

* Thu Apr 11 2019 ryan woodsmall <rwoodsmall@gmail.com>
- release bump for musl 1.1.22

* Tue Jan 22 2019 ryan woodsmall <rwoodsmall@gmail.com>
- release no. bump for musl-libc 1.1.21

* Mon Dec  3 2018 ryan woodsmall <rwoodsmall@gmail.com>
- bump editline version
- comment out conflicts/provides

* Tue Sep 11 2018 ryan woodsmall <rwoodsmall@gmail.com>
- release no. bump for musl-libc 1.1.20

* Thu Feb 22 2018 ryan woodsmall <rwoodsmall@gmail.com>
- release no. bump for musl-libc 1.1.19

* Fri Feb  9 2018 ryan woodsmall <rwoodsmall@gmail.com> 
- static build with musl and including editline

* Wed May 13 2015 Robert Scheck <robert@fedoraproject.org> 1.7.4-1
- Upgrade to 1.7.4

* Sat May 09 2015 Robert Scheck <robert@fedoraproject.org> 1.7.3-1
- Upgrade to 1.7.3

* Wed Apr 08 2015 Robert Scheck <robert@fedoraproject.org> 1.7.2-1
- Upgrade to 1.7.2
- Initial spec file for Fedora and Red Hat Enterprise Linux
