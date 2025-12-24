Name:           petclinic
Version:        1.0
Release:        1%{?dist}
Summary:        Spring Boot Petclinic Application

License:        GPL
URL:            http://example.com
BuildArch:      noarch

Requires:       java-17-openjdk

# Source files provided in rpmbuild/SOURCES/
Source0:        petclinic.jar
Source1:        application.properties
Source2:        petclinic.service

%description
Spring Boot Petclinic packaged as an RPM.

%pre
# Create user if not exists
id petclinic &>/dev/null || useradd -r -s /bin/false -d /opt/petclinic petclinic

%install
# Create required directories
mkdir -p %{buildroot}/opt/petclinic
mkdir -p %{buildroot}/etc/petclinic
mkdir -p %{buildroot}/var/log/petclinic
mkdir -p %{buildroot}/etc/systemd/system

# Copy application JAR
install -m 644 %{SOURCE0} %{buildroot}/opt/petclinic/petclinic.jar

# Copy application.properties
install -m 644 %{SOURCE1} %{buildroot}/etc/petclinic/application.properties

# Copy service file
install -m 644 %{SOURCE2} %{buildroot}/etc/systemd/system/petclinic.service

%files
/opt/petclinic/petclinic.jar
/etc/petclinic/application.properties
/etc/systemd/system/petclinic.service
/var/log/petclinic/

%defattr(-,petclinic,petclinic,-)

%post
# Reload systemd to pick up the new service
systemctl daemon-reload

# Enable service so it starts on next reboot
systemctl enable petclinic || true

# Assign correct ownership to all app folders
chown -R petclinic:petclinic /opt/petclinic
chown -R petclinic:petclinic /etc/petclinic
chown -R petclinic:petclinic /var/log/petclinic

# Set permissions
chmod 755 /opt/petclinic
chmod 750 /etc/petclinic
chmod 755 /var/log/petclinic
chmod 644 /etc/petclinic/application.properties
chmod 644 /etc/systemd/system/petclinic.service

%preun
# Stop service before uninstall
systemctl stop petclinic || true

%postun
# Reload systemd after uninstall
systemctl daemon-reload

# Cleanup service file
rm -f /etc/systemd/system/petclinic.service || true

# Cleanup directories
rm -rf /opt/petclinic || true
rm -rf /etc/petclinic || true
rm -rf /var/log/petclinic || true