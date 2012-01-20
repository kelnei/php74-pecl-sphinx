%global php_apiver  %((echo 0; php -i 2>/dev/null | sed -n 's/^PHP API => //p') | tail -1)
%{!?__pecl:     %{expand: %%global __pecl     %{_bindir}/pecl}}
%{!?php_extdir: %{expand: %%global php_extdir %(php-config --extension-dir)}}

%define pecl_name sphinx

Name:		php-pecl-sphinx
Version:	1.1.0
Release:	3%{?dist}
Summary:	PECL extension for Sphinx SQL full-text search engine
Group:		Development/Languages
License:	PHP
URL:		http://pecl.php.net/package/%{pecl_name}
Source0:	http://pecl.php.net/get/%{pecl_name}-%{version}.tgz
# https://bugs.php.net/60349
Patch0:         sphinx-php54.patch

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:	libsphinxclient-devel
BuildRequires:  php-pear
BuildRequires:	php-devel >= 5.1.3
Requires:       php(zend-abi) = %{php_zend_api}
Requires:       php(api) = %{php_core_api}
Requires(post): %{__pecl}
Requires(postun): %{__pecl}

Provides:       php-pecl(%{pecl_name}) = %{version}

# RPM 4.8
%{?filter_provides_in: %filter_provides_in %{php_extdir}/.*\.so$}
%{?filter_setup}
# RPM 4.9
%global __provides_exclude_from %{?__provides_exclude_from:%__provides_exclude_from|}%{php_extdir}/.*\\.so$


%description
This extension provides PHP bindings for libsphinxclient, 
client library for Sphinx the SQL full-text search engine.

%prep
%setup -q -c
%patch0 -p0 -b .php54

# Upstream often forget this
extver=$(sed -n '/#define PHP_SPHINX_VERSION/{s/.* "//;s/".*$//;p}' %{pecl_name}-%{version}/php_sphinx.h)
if test "x${extver}" != "x%{version}"; then
   : Error: Upstream version is ${extver}, expecting %{version}.
   exit 1
fi

[ -f package2.xml ] || %{__mv} package.xml package2.xml
%{__mv} package2.xml %{pecl_name}-%{version}/%{pecl_name}.xml


%build
cd %{pecl_name}-%{version}
phpize
%configure
%{__make} %{?_smp_mflags}

%check
# simple module load test
cd %{pecl_name}-%{version}
php --no-php-ini \
    --define extension_dir=modules \
    --define extension=%{pecl_name}.so \
    --modules | grep %{pecl_name}


%install
cd %{pecl_name}-%{version}
%{__rm} -rf %{buildroot}
%{__make} install INSTALL_ROOT=%{buildroot} INSTALL="install -p"

%{__mkdir_p} %{buildroot}%{_sysconfdir}/php.d
%{__cat} > %{buildroot}%{_sysconfdir}/php.d/%{pecl_name}.ini << 'EOF'
; Enable %{pecl_name} extension module
extension=%{pecl_name}.so
EOF

%{__mkdir_p} %{buildroot}%{pecl_xmldir}
%{__install} -p -m 644 %{pecl_name}.xml %{buildroot}%{pecl_xmldir}/%{name}.xml


%clean
%{__rm} -rf %{buildroot}

%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ]  ; then
%{pecl_uninstall} %{pecl_name} >/dev/null || :
fi

%files
%defattr(-,root,root,-)
%doc %{pecl_name}-%{version}/CREDITS
%config(noreplace) %{_sysconfdir}/php.d/%{pecl_name}.ini
%{php_extdir}/%{pecl_name}.so
%{pecl_xmldir}/%{name}.xml


%changelog
* Thu Jan 19 2012 Remi Collet <remi@fedoraproject.org> - 1.1.0-3
- build against php 5.4, with patch
- add filter to fix private-shared-object-provides

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Jul 15 2011 Andrew Colin Kissa <andrew@topdog.za.net> - 1.1.0-1
- Update to latest upstream
- Fix bugzilla #715830

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Sep 06 2009 Andrew Colin Kissa <andrew@topdog.za.net> - 1.0.0-2
- Add checks
- Add php-devel version requirement

* Mon Aug 05 2009 Andrew Colin Kissa <andrew@topdog.za.net> - 1.0.0-1
- Initial package
