#!/bin/bash

set -e

SCRIPTS=(apache_dos asn_info auth_detection call_by_ip check_as_peers check_ssh_version cms_detection dns_a dns_a_nr dns_afxr dns_b_nr dns_dom_mx dns_find_ns dns_hosting dns_reverse_lookup dns_soa dns_spf dns_top_tlds doc_files_crawler ftp_bruteforce fuzz_check google_search_email grep_url http_banner http_dos icmp_ip_id joomla_scan linked_partners login_pages nic_typosquatting nic_whois nikto nmap_tcp nmap_tcp_os nmap_udp ns_version params_crawler ping redirects renegotiation smtp_auth smtp_banner smtp_dnsbl smtp_filter smtp_relay smtp_starttls smtp_user_verification snmp_community sql_injector ssh_bruteforce ssl_cert_usage ssl_certificate ssl_ciphers ssl_key_size ssl_quality ssl_test ssl_validity subdomain_bruteforce tcp_timestamp tcp_traceroute theharvester_emails udp_traceroute urlscan user_dirs_access w3af_ajax w3af_bing_spider w3af_blank_body w3af_code_disclosure w3af_collect_cookies w3af_detect_reverse_proxy w3af_detect_transparent_proxy w3af_directory_indexing w3af_dom_xss w3af_domain_dot w3af_dot_net_errors w3af_dot_net_event_validation w3af_favicon_identification w3af_feeds w3af_file_upload w3af_find_captchas w3af_find_comments w3af_finger_bing w3af_finger_google w3af_finger_pks w3af_form_autocomplete w3af_get_mails w3af_ghdb w3af_halberd w3af_hash_find w3af_http_auth_detect w3af_http_in_body w3af_meta_tags w3af_objects w3af_path_disclosure w3af_phishtank w3af_private_ip w3af_ria_enumerator w3af_robots_reader w3af_sitemap_reader w3af_strange_http_code w3af_svn_users w3af_zone_h web_http_methods web_sql_xss websearch_client_domains webserver_error_msg webserver_files webserver_ssl www_auth_scanner www_dir_scanner www_file_scanner)

for SCRIPT in "${SCRIPTS[@]}"; do
    echo $SCRIPT
    echo "-----"

    if [ ! -f "/tmp/.skip-$SCRIPT" ]; then
        vzctl exec2 666 "python /opt/gtta/run_script.py $SCRIPT --test"
        echo ""

        touch /tmp/.skip-$SCRIPT

        sleep 3
    else
        echo "skipping..."
        echo ""
    fi
done
