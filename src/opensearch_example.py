from opensearchpy import OpenSearch
from opensearch_dsl import Search

def main():
	host = 'localhost'
	port = 9200
	auth = ('admin', '!UL234zxc')  # For testing only. Don't store credentials in code.

	# Create the client with SSL/TLS enabled, but hostname verification disabled.
	client = OpenSearch(
		hosts=[{'host': host, 'port': port}],
		http_compress=True,  # enables gzip compression for request bodies
		http_auth=auth,
		use_ssl=True,
		verify_certs=False,
		ssl_assert_hostname=False,
		ssl_show_warn=False
	)

	info = client.info()
	valid = False

if __name__ == "__main__":
	main()
