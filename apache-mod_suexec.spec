%if %mandriva_branch == Cooker
# Cooker
%define release %mkrel 1
%else
# Old distros
%define subrel 1
%define release %mkrel 1
%endif

%define mod_name mod_suexec
%define mod_conf 69_%{mod_name}.conf
%define mod_so %{mod_name}.so
%define sourcename %{mod_name}-%{apache_version}

Summary:	Allows CGI scripts to run as a specified user and Group
Name:		apache-%{mod_name}
Version:	2.4.2
Release:	%release
Group:		System/Servers
License:	Apache License
URL:		http://httpd.apache.org/docs/suexec.html
Source1:	%{mod_conf}
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):  apache-conf >= %{version}
Requires(pre):  apache >= %{version}
Requires:	apache-conf >= %{version}
Requires:	apache >= %{version}
BuildRequires:  apache-devel >= %{version}
BuildRequires:  apache-source >= %{version}
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
This module, in combination with the suexec support program
allows CGI scripts to run as a specified user and Group.

Normally, when a CGI or SSI program executes, it runs as the
same user who is running the web server.

%prep

%setup -c -T -n %{name}

cp %{_includedir}/apache/*.h .
cp -rp `apr-1-config --includedir`/* .
cp -rp `apu-1-config --includedir`/* .

echo "#define AP_GID_MIN 100"  >> ap_config_auto.h
echo "#define AP_UID_MIN 100"  >> ap_config_auto.h
echo "#define AP_DOC_ROOT \"%{_var}/www\"" >> ap_config_auto.h
echo "#define AP_HTTPD_USER \"apache\""  >> ap_config_auto.h
echo "#define AP_LOG_EXEC \"%{_var}/log/httpd/suexec_log\""  >> ap_config_auto.h
echo "#define AP_SAFE_PATH \"/usr/local/bin:/usr/bin:/bin\""  >> ap_config_auto.h
echo "#define AP_SUEXEC_UMASK 0077"  >> ap_config_auto.h
echo "#define AP_USERDIR_SUFFIX \"public_html\""  >> ap_config_auto.h

cp %{_usrsrc}/apache-%{version}/docs/man/suexec.8 .
cp %{_usrsrc}/apache-%{version}/docs/manual/mod/mod_suexec.html.en mod_suexec.html
cp %{_usrsrc}/apache-%{version}/docs/manual/programs/suexec.html.en programs-suexec.html
cp %{_usrsrc}/apache-%{version}/docs/manual/suexec.html.en suexec.html
cp %{_usrsrc}/apache-%{version}/modules/generators/mod_suexec.c .
cp %{_usrsrc}/apache-%{version}/modules/generators/mod_suexec.h .
cp %{_usrsrc}/apache-%{version}/support/suexec.c .
cp %{_usrsrc}/apache-%{version}/support/suexec.h .

cp %{SOURCE1} %{mod_conf}

%build

gcc `%{_bindir}/apxs -q CFLAGS -Wall` -D_REENTRANT -D_GNU_SOURCE -D_LARGEFILE_SOURCE -D_LARGEFILE64_SOURCE -I. -o suexec suexec.c

%{_bindir}/apxs -I. -c %{mod_name}.c

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_mandir}/man8

install -m0755 suexec %{buildroot}%{_sbindir}/suexec
install suexec.8 %{buildroot}%{_mandir}/man8/suexec.8

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}


cat > README.MDK << EOF
#!/bin/sh
# 
# This file shows how you can build a customised %{_sbindir}/suexec binary.
#
# It requires that you have additional development packages installed:
# urpmi apache-devel >= %{apache_version}
# urpmi apache-source >= %{apache_version}

gcc \`%{_sbindir}/apxs -q CFLAGS -Wall\` -D_REENTRANT -D_GNU_SOURCE -D_LARGEFILE_SOURCE -D_LARGEFILE64_SOURCE \\
    -I%{_includedir}/apache -I%{_usrsrc}/apache-%{version}/support \\
    \`apr-1-config --includes\` \`apu-1-config --includes\` \\
    -DAP_GID_MIN=100 -DAP_UID_MIN=100 -DAP_DOC_ROOT=\"/home\" -DAP_HTTPD_USER=\"apache\" \\
    -DAP_LOG_EXEC=\"%{_var}/log/httpd/suexec_log\" \\
    -DAP_SAFE_PATH=\"/usr/local/bin:/usr/bin:/bin\" \\
    -DAP_SUEXEC_UMASK=0077 -DAP_USERDIR_SUFFIX=\"public_html\" \\
    -o %{_sbindir}/suexec %{_usrsrc}/apache-%{version}/support/suexec.c

chown root:apache %{_sbindir}/suexec
chmod 4710 %{_sbindir}/suexec
%{_sbindir}/suexec -V

EOF

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
        %{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc mod_suexec.html suexec.html README.MDK
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache/%{mod_so}
%attr(4710,root,apache) %{_sbindir}/suexec
%{_mandir}/man8/*


%changelog
* Wed Feb 01 2012 Oden Eriksson <oeriksson@mandriva.com> 2.2.22-0.1
- built for updates

* Wed Feb 01 2012 Oden Eriksson <oeriksson@mandriva.com> 2.2.22-1mdv2012.0
+ Revision: 770411
- 2.2.22
- make it backportable

* Wed Sep 14 2011 Oden Eriksson <oeriksson@mandriva.com> 2.2.21-1
+ Revision: 699748
- 2.2.21

* Thu Sep 01 2011 Oden Eriksson <oeriksson@mandriva.com> 2.2.20-1
+ Revision: 697667
- 2.2.20

* Tue Jun 14 2011 Oden Eriksson <oeriksson@mandriva.com> 2.2.19-1
+ Revision: 684992
- bump release

* Sat May 21 2011 Oden Eriksson <oeriksson@mandriva.com> 2.2.19-0
+ Revision: 676779
- 2.2.19 (pre-release)

* Sat May 14 2011 Oden Eriksson <oeriksson@mandriva.com> 2.2.18-1
+ Revision: 674419
- 2.2.18

* Mon May 02 2011 Oden Eriksson <oeriksson@mandriva.com> 2.2.17-2
+ Revision: 662779
- mass rebuild

* Wed Oct 20 2010 Oden Eriksson <oeriksson@mandriva.com> 2.2.17-1mdv2011.0
+ Revision: 586898
- 2.2.17
- 2.2.17

* Sat Mar 06 2010 Oden Eriksson <oeriksson@mandriva.com> 2.2.15-1mdv2010.1
+ Revision: 515161
- 2.2.15 (official)

* Tue Mar 02 2010 Oden Eriksson <oeriksson@mandriva.com> 2.2.15-0.0mdv2010.1
+ Revision: 513533
- 2.2.15 (pre-release)

* Sun Oct 04 2009 Oden Eriksson <oeriksson@mandriva.com> 2.2.14-1mdv2010.0
+ Revision: 453382
- 2.2.14 was silently released 23-Sep-2009

* Wed Sep 30 2009 Oden Eriksson <oeriksson@mandriva.com> 2.2.14-0.1mdv2010.0
+ Revision: 451694
- 2.2.14 (pre-release)

* Mon Aug 10 2009 Oden Eriksson <oeriksson@mandriva.com> 2.2.13-1mdv2010.0
+ Revision: 414349
- 2.2.13

* Wed Jul 29 2009 Oden Eriksson <oeriksson@mandriva.com> 2.2.12-1mdv2010.0
+ Revision: 402993
- 2.2.12

* Tue Dec 16 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.11-1mdv2009.1
+ Revision: 314832
- 2.2.11

* Mon Oct 20 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.10-1mdv2009.1
+ Revision: 295607
- 2.2.10

* Fri Jun 13 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.9-1mdv2009.0
+ Revision: 218818
- 2.2.9

* Thu Jun 05 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.8-3mdv2009.0
+ Revision: 215300
- rebuild

* Fri Mar 07 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.8-2mdv2008.1
+ Revision: 181443
- rebuild

* Fri Jan 18 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.8-1mdv2008.1
+ Revision: 154719
- 2.2.8 (official release)

* Fri Jan 11 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.8-0.1mdv2008.1
+ Revision: 147925
- 2.2.8

* Sun Jan 06 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.7-0.1mdv2008.1
+ Revision: 146091
- fix build
- 2.2.7

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Wed Sep 19 2007 Oden Eriksson <oeriksson@mandriva.com> 2.2.6-2mdv2008.0
+ Revision: 90962
- this is no third party module, so put it in the right place

* Sat Sep 08 2007 Oden Eriksson <oeriksson@mandriva.com> 2.2.6-1mdv2008.0
+ Revision: 82352
- 2.2.6 (release)

* Thu Aug 16 2007 Oden Eriksson <oeriksson@mandriva.com> 2.2.5-0.1mdv2008.0
+ Revision: 64324
- use the new %%serverbuild macro

* Wed Jun 13 2007 Oden Eriksson <oeriksson@mandriva.com> 2.2.4-4mdv2008.0
+ Revision: 38416
- rebuild


* Sat Mar 10 2007 Oden Eriksson <oeriksson@mandriva.com> 2.2.4-3mdv2007.1
+ Revision: 140587
- rebuild

* Tue Feb 27 2007 Oden Eriksson <oeriksson@mandriva.com> 2.2.4-2mdv2007.1
+ Revision: 126624
- general cleanups

* Sat Feb 10 2007 Oden Eriksson <oeriksson@mandriva.com> 2.2.4-1mdv2007.1
+ Revision: 118724
- 2.2.4

* Thu Nov 16 2006 Oden Eriksson <oeriksson@mandriva.com> 2.2.3-3mdv2007.1
+ Revision: 84877
- rebuild
- rebuild
- Import apache-mod_suexec

* Sat Jul 29 2006 Oden Eriksson <oeriksson@mandriva.com> 2.2.3-1mdk
- 2.2.3

* Mon May 15 2006 Oden Eriksson <oeriksson@mandriva.com> 2.2.2-1mdk
- 2.2.2

* Mon Dec 12 2005 Oden Eriksson <oeriksson@mandriva.com> 2.2.0-1mdk
- 2.2.0

* Sun Oct 30 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.55-3mdk
- rebuilt to provide a -debug package too

* Mon Oct 17 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.55-2mdk
- rebuilt against correct apr-0.9.7

* Sat Oct 15 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.55-1mdk
- rebuilt for apache-2.0.55

* Tue Aug 02 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54-4mdk
- fix minor bug

* Sat Jul 30 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54-3mdk
- added another work around for a rpm bug

* Sat Jul 30 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54-2mdk
- added a work around for a rpm bug, "Requires(foo,bar)" don't work

* Fri May 27 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54-1mdk
- rename the package
- the conf.d directory is renamed to modules.d
- use new rpm-4.4.x pre,post magic

* Thu Mar 31 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53-7mdk
- provide an example how to build a customised suexec binary

* Thu Mar 17 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53-6mdk
- use the %%mkrel macro

* Sun Feb 27 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53-5mdk
- fix %%post and %%postun to prevent double restarts

* Wed Feb 16 2005 Stefan van der Eijk <stefan@eijk.nu> 2.0.53-4mdk
- fix bug #6574

* Wed Feb 16 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53-3mdk
- fix deps

* Tue Feb 15 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53-2mdk
- spec file cleanups, remove the ADVX-build stuff

* Tue Feb 08 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53-1mdk
- rebuilt for apache 2.0.53

* Fri Sep 17 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.50-1mdk
- rebuilt

* Wed Aug 11 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.50-3mdk
- rebuilt

* Tue Jul 13 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.50-2mdk
- remove redundant provides

* Thu Jul 01 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.50-1mdk
- built for apache 2.0.50

* Sat Jun 12 2004 Oden Eriksson <oden.eriksson@kvikkjokk.net> 2.0.49-1mdk
- rebuilt for apache v2.0.49
- use ap*-config --includedir to get headers

