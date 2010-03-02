%define mod_name mod_suexec
%define mod_conf 69_%{mod_name}.conf
%define mod_so %{mod_name}.so
%define sourcename %{mod_name}-%{apache_version}

Summary:	Allows CGI scripts to run as a specified user and Group
Name:		apache-%{mod_name}
Version:	2.2.15
Release:	%mkrel 0.0
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

gcc `%{_sbindir}/apxs -q CFLAGS -Wall` -D_REENTRANT -D_GNU_SOURCE -D_LARGEFILE_SOURCE -D_LARGEFILE64_SOURCE -I. -o suexec suexec.c

%{_sbindir}/apxs -I. -c %{mod_name}.c

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
