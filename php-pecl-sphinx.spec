# we don't want -z defs linker flag
%undefine _strict_symbol_defs_build

# https://github.com/php/pecl-search_engine-sphinx/tree/php7
%global gh_commit   201eb00bd370bf8ff2d5787ac1a1b588f14af5a0
%global gh_short    %(c=%{gh_commit}; echo ${c:0:7})
%global gh_owner    php
%global gh_project  pecl-search_engine-sphinx
%global gh_date     20170203

%global pecl_name   sphinx
%global with_zts    0%{!?_without_zts:%{?__ztsphp:1}}
%global ini_name    40-%{pecl_name}.ini

Name:		php-pecl-sphinx
Version:	1.4.0
%if 0%{?gh_date:1}
Release:	0.7.%{gh_date}git%{gh_short}%{?dist}
%else
Release:	11%{?dist}
%endif
Summary:	PECL extension for Sphinx SQL full-text search engine
Group:		Development/Languages
License:	PHP
URL:		http://pecl.php.net/package/%{pecl_name}
%if 0%{?gh_date:1}
Source0:	https://github.com/%{gh_owner}/%{gh_project}/archive/%{gh_commit}/%{pecl_name}-%{version}-%{gh_short}.tar.gz
%else
Source0:	http://pecl.php.net/get/%{pecl_name}-%{version}.tgz
%endif

BuildRequires:	libsphinxclient-devel
BuildRequires:  php-pear
BuildRequires:	php-devel >= 7
Requires:       php(zend-abi) = %{php_zend_api}
Requires:       php(api) = %{php_core_api}

Provides:       php-%{pecl_name} = %{version}
Provides:       php-%{pecl_name}%{?_isa} = %{version}
Provides:       php-pecl(%{pecl_name}) = %{version}
Provides:       php-pecl(%{pecl_name})%{?_isa} = %{version}


%description
This extension provides PHP bindings for libsphinxclient, 
client library for Sphinx the SQL full-text search engine.

%prep
%setup -q -c
%if 0%{?gh_date:1}
mv %{gh_project}-%{gh_commit} NTS
%{__php} -r '
  $pkg = simplexml_load_file("NTS/package.xml");
  $pkg->date = substr("%{gh_date}",0,4)."-".substr("%{gh_date}",4,2)."-".substr("%{gh_date}",6,2);
  $pkg->version->release = "%{version}dev";
  $pkg->stability->release = "devel";
  $pkg->asXML("package.xml");
'
%else
mv %{pecl_name}-%{version} NTS
%endif

sed -e '/LICENSE/s/role="doc"/role="src"/' -i package.xml

cd NTS
# Upstream often forget this
extver=$(sed -n '/#define PHP_SPHINX_VERSION/{s/.* "//;s/".*$//;p}' php_sphinx.h)
if test "x${extver}" != "x%{version}%{?gh_date:-dev}"; then
   : Error: Upstream version is ${extver}, expecting %{version}%{?gh_date:-dev}.
   exit 1
fi
cd ..

cat > %{ini_name} << 'EOF'
; Enable %{pecl_name} extension module
extension=%{pecl_name}.so
EOF

%if %{with_zts}
# duplicate for ZTS build
cp -pr NTS ZTS
%endif


%build
cd NTS
%{_bindir}/phpize
%configure  --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}

%if %{with_zts}
cd ../ZTS
%{_bindir}/zts-phpize
%configure  --with-php-config=%{_bindir}/zts-php-config
make %{?_smp_mflags}
%endif


%check
: simple module load test for the NTS extension
%{__php} --no-php-ini \
    --define extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}

%if %{with_zts}
: simple module load test for the ZTS extension
%{__ztsphp} --no-php-ini \
    --define extension=%{buildroot}%{php_ztsextdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}
%endif


%install
make -C NTS install INSTALL_ROOT=%{buildroot}

# Install XML package description
install -Dpm 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

# install config file
install -Dpm644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

%if %{with_zts}
# Install the ZTS stuff
make -C ZTS install INSTALL_ROOT=%{buildroot}
install -Dpm644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif

# Documentation
cd NTS
for i in $(grep 'role="doc"' ../package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 $i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%files
%license NTS/LICENSE
%doc %{pecl_docdir}/%{pecl_name}
%{pecl_xmldir}/%{name}.xml

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so

%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{pecl_name}.so
%endif


%changelog
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
