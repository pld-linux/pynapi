Summary:	pynapi - Movie Subtitle Downloader
Summary(pl.UTF-8):	pynapi - narzędzie do ściągania napisów do filmów
Name:		pynapi
Version:	0.20
Release:	3
License:	GPL v3+
Group:		Applications/Multimedia
Source0:	pynapi.py
BuildRequires:	python-modules
BuildRequires:	rpm-pythonprov
%pyrequires_eq  python-modules
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Command line NAPI-PROJEKT and NAPISY24 subtitles downloader.

%description -l pl.UTF-8
Obsługiwane z linii poleceń narzędzie do ściągania napisów z projektu
NAPI oraz NAPISY24.

%prep
%setup -q -c -T

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_bindir}

install %{SOURCE0} $RPM_BUILD_ROOT%{_bindir}/pynapi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/pynapi
