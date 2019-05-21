# IUS spec file for php73-pecl-sphinx, forked from:
#
# we don't want -z defs linker flag
%undefine _strict_symbol_defs_build

# https://github.com/ClassifiedAds/pecl-search_engine-sphinx
%global gh_project  pecl-search_engine-sphinx
%global pecl_name   sphinx
%global ini_name    40-%{pecl_name}.ini
%global php         php73

%bcond_with zts

Name:       %{php}-pecl-%{pecl_name}
Version:    3.1.1
Release:    1%{?dist}
Summary:    PECL extension for Sphinx SQL full-text search engine
Group:      Development/Languages
License:    PHP
URL:        https://pecl.php.net/package/%{pecl_name}
Source0:    https://github.com/ClassifiedAds/%{gh_project}/releases/download/%{pecl_name}-%{version}/%{pecl_name}-%{version}.tgz

BuildRequires:  libsphinxclient-devel
BuildRequires:  %{php}-devel
BuildRequires:  pear1

Requires:       php(api) = %{php_core_api}
Requires:       php(zend-abi) = %{php_zend_api}

Provides:       php-%{pecl_name} = %{version}
Provides:       php-%{pecl_name}%{?_isa} = %{version}
Provides:       php-pecl(%{pecl_name}) = %{version}
Provides:       php-pecl(%{pecl_name})%{?_isa} = %{version}

Provides:       php-pecl-sphinx = %{version}-%{release}
Provides:       php-pecl-sphinx%{?_isa} = %{version}-%{release}
Conflicts:      php-pecl-sphinx% < %{version}-%{release}


%description
This extension provides PHP bindings for libsphinxclient, 
client library for Sphinx the SQL full-text search engine.


%prep
%setup -q -c
mv %{pecl_name}-%{version} NTS

sed -e '/LICENSE/s/role="doc"/role="src"/' -i package.xml

# Upstream often forget this
extver=$(sed -n '/#define PHP_SPHINX_VERSION/{s/.* "//;s/".*$//;p}' NTS/php_sphinx.h)
if test "x${extver}" != "x%{version}"; then
   : Error: Upstream version is ${extver}, expecting %{version}.
   exit 1
fi

cat > %{ini_name} << 'EOF'
; Enable %{pecl_name} extension module
extension=%{pecl_name}.so
EOF

%if %{with zts}
# duplicate for ZTS build
cp -pr NTS ZTS
%endif


%build
pushd NTS
%{_bindir}/phpize
%configure  --with-php-config=%{_bindir}/php-config
%make_build
popd

%if %{with zts}
pushd ZTS
%{_bindir}/zts-phpize
%configure  --with-php-config=%{_bindir}/zts-php-config
%make_build
popd
%endif


%check
: simple module load test for the NTS extension
%{__php} --no-php-ini \
    --define extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}

%if %{with zts}
: simple module load test for the ZTS extension
%{__ztsphp} --no-php-ini \
    --define extension=%{buildroot}%{php_ztsextdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}
%endif


%install
make -C NTS install INSTALL_ROOT=%{buildroot}

# Install XML package description
install -D -p -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{pecl_name}.xml

# install config file
install -D -p -m 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

%if %{with zts}
# Install the ZTS stuff
make -C ZTS install INSTALL_ROOT=%{buildroot}
install -D -p -m 644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif

# Documentation
for i in $(grep 'role="doc"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -D -p -m 644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%triggerin -- pear1
if [ -x %{__pecl} ]; then
    %{pecl_install} %{pecl_xmldir}/%{pecl_name}.xml >/dev/null || :
fi


%posttrans
if [ -x %{__pecl} ]; then
    %{pecl_install} %{pecl_xmldir}/%{pecl_name}.xml >/dev/null || :
fi


%postun
if [ $1 -eq 0 -a -x %{__pecl} ]; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%files
%license NTS/LICENSE
%doc %{pecl_docdir}/%{pecl_name}
%{pecl_xmldir}/%{pecl_name}.xml

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so

%if %{with zts}
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{pecl_name}.so
%endif


%changelog
* Tue May 21 2019 Matt Linscott <matt.linscott@gmail.com> - 3.1.1-1
- Rebuild repackaged upstream
- Remove patch

* Fri May 10 2019 Matt Linscott <matt.linscott@mgail.com> - 1.4.0-0.8.20170203gitd958afb
- Patch sphinx.c to remove methods remove from libsphinxclient 

* Thu May 09 2019 Matt Linscott <matt.linscott@gmail.com> - 1.4.0-0.8.20170203gitd958afb
- Port from Fedora to IUS
- Install package.xml as %%{pecl_name}.xml, not %%{name}.xml
- Add pear1 and scriptlets

* Thu Oct 11 2018 Remi Collet <remi@remirepo.net> - 1.4.0-0.8.20170203git201eb00
- Rebuild for https://fedoraproject.org/wiki/Changes/php73

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.0-0.7.20170203git201eb00
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.0-0.6.20170203git201eb00
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Jan 25 2018 Remi Collet <remi@remirepo.net> - 1.4.0-0.5.20170203git201eb00
- undefine _strict_symbol_defs_build

* Tue Oct 03 2017 Remi Collet <remi@fedoraproject.org> - 1.4.0-0.4.20170203git201eb00
- rebuild for https://fedoraproject.org/wiki/Changes/php72

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.0-0.3.20170203git201eb00
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.0-0.2.20170203git201eb00
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Remi Collet <remi@remirepo.net> - 1.4.0-0.1.20170203git201eb00
- update to 1.4.0-dev (git snapshot) for PHP 7
- fix license installation

* Sat Feb 13 2016 Remi Collet <remi@fedoraproject.org> - 1.3.2-6
- F24: drop scriptlets (replaced by file triggers in php-pear)

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Nov 12 2014 Dan Horák <dan[at]danny.cz> - 1.3.2-3
- drop ExclusiveArch, sphinx has been fixed

* Wed Oct 29 2014 Remi Collet <rcollet@fedoraproject.org> - 1.3.2-2
- set ExclusiveArch, as sphinx (detected by Koschei)

* Fri Aug 29 2014 Remi Collet <rcollet@fedoraproject.org> - 1.3.2-1
- update to 1.3.2
- install doc in pecl_docdir
- add LICENSE provided by upstream
- enable ZTS build
- provides php-sphinx
- fix private shared filter

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jun 19 2014 Remi Collet <rcollet@redhat.com> - 1.2.0-4
- rebuild for https://fedoraproject.org/wiki/Changes/Php56
- add numerical prefix to extension configuration file

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Mar 22 2013 Remi Collet <rcollet@redhat.com> - 1.1.0-6
- update to 1.2.0
- rebuild for http://fedoraproject.org/wiki/Features/Php55

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

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

* Wed Aug 05 2009 Andrew Colin Kissa <andrew@topdog.za.net> - 1.0.0-1
- Initial package
