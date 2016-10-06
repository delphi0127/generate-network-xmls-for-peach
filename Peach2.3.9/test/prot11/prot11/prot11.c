// prot11.cpp : Defines the entry point for the console application.
//

#include <winsock2.h>
#include <ws2tcpip.h>
#include <stdlib.h>
#include <stdio.h>

#define DEFAULT_BUFLEN 512
#define DEFAULT_PORT "27016"

//#pragma push pack
//#pragma pack(1)
struct _chunk
{
	unsigned int	type;
	unsigned int	size;
	unsigned char	data[12];
};

struct _header
{
	unsigned int	version;
	unsigned int	size;
	unsigned int	chunkCount;
	struct _chunk	chunks[];
};

//#pragma pop pack

void server();
void client(int argc, char** argv);
void PrintPacket(struct _header* pkt);
struct _header* CreatePacket();

int main(int argc, char** argv)
{
	if(!strcmp(argv[1], "-s"))
	{
		server();
	}
	else
	{
		client(argc, argv);
	}

	return 0;
}

void server()
{
	struct _header* pkt;
	WSADATA wsaData;
	SOCKET ListenSocket = INVALID_SOCKET,
		ClientSocket = INVALID_SOCKET;
	struct addrinfo *result = NULL,
		hints;
	char recvbuf[DEFAULT_BUFLEN];
	int iResult, iSendResult;
	int recvbuflen = DEFAULT_BUFLEN;


	// Initialize Winsock
	iResult = WSAStartup(MAKEWORD(2,2), &wsaData);
	if (iResult != 0) {
		printf("WSAStartup failed: %d\n", iResult);
		return;
	}

	ZeroMemory(&hints, sizeof(hints));
	hints.ai_family = AF_INET;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_protocol = IPPROTO_TCP;
	hints.ai_flags = AI_PASSIVE;

	// Resolve the server address and port
	iResult = getaddrinfo(NULL, DEFAULT_PORT, &hints, &result);
	if ( iResult != 0 ) {
		printf("getaddrinfo failed: %d\n", iResult);
		WSACleanup();
		return;
	}

	// Create a SOCKET for connecting to server
	ListenSocket = socket(result->ai_family, result->ai_socktype, result->ai_protocol);
	if (ListenSocket == INVALID_SOCKET) {
		printf("socket failed: %ld\n", WSAGetLastError());
		freeaddrinfo(result);
		WSACleanup();
		return;
	}

	// Setup the TCP listening socket
	iResult = bind( ListenSocket, result->ai_addr, (int)result->ai_addrlen);
	if (iResult == SOCKET_ERROR) {
		printf("bind failed: %d\n", WSAGetLastError());
		freeaddrinfo(result);
		closesocket(ListenSocket);
		WSACleanup();
		return;
	}

	freeaddrinfo(result);

	while(1)
	{

		iResult = listen(ListenSocket, SOMAXCONN);
		if (iResult == SOCKET_ERROR) {
			printf("listen failed: %d\n", WSAGetLastError());
			closesocket(ListenSocket);
			WSACleanup();
			return;
		}

		// Accept a client socket
		ClientSocket = accept(ListenSocket, NULL, NULL);
		if (ClientSocket == INVALID_SOCKET) {
			printf("accept failed: %d\n", WSAGetLastError());
			closesocket(ListenSocket);
			WSACleanup();
			return;
		}

		// No longer need server socket
		//closesocket(ListenSocket);

		// Receive until the peer shuts down the connection
		do {

			iResult = recv(ClientSocket, recvbuf, recvbuflen, 0);
			if (iResult > 0) {
				printf("Bytes received: %d\n", iResult);

				// Echo the buffer back to the sender
				PrintPacket((struct _header*)recvbuf);
				
				pkt = CreatePacket();
				iSendResult = send( ClientSocket, (char*)pkt, pkt->size, 0 );
				if (iSendResult == SOCKET_ERROR) {
					printf("send failed: %d\n", WSAGetLastError());
					closesocket(ClientSocket);
					WSACleanup();
					return;
				}

				free(pkt);

				printf("Bytes sent: %d\n", iSendResult);
				
			}
			else if (iResult == 0)
				printf("Connection closing...\n");
			else  {
				printf("recv failed: %d\n", WSAGetLastError());
				closesocket(ClientSocket);
				WSACleanup();
				return;
			}

		} while (iResult > 0);

		// shutdown the connection since we're done
		iResult = shutdown(ClientSocket, SD_SEND);
		if (iResult == SOCKET_ERROR) {
			printf("shutdown failed: %d\n", WSAGetLastError());
			closesocket(ClientSocket);
			WSACleanup();
			return;
		}
		// cleanup
		closesocket(ClientSocket);

	}
	WSACleanup();
}

void PrintPacket(struct _header* pkt)
{
	int i;

	printf("=================\n");
	printf("Packet version: %u\n", (unsigned int)pkt->version);
	printf("Packet size: %u\n", pkt->size);
	printf("Number of chunks: %u\n", pkt->chunkCount);

	for(i = 0; i<pkt->chunkCount; i++)
	{
		printf("%d: Chunk type: %u\n", i, (unsigned int)pkt->chunks[i].type);
		printf("%d: Chunk size: %u\n", i, pkt->chunks[i].size);
		printf("%d: Chunk data: %s\n", i, pkt->chunks[i].data);
	}

	printf("=================\n");
}

struct _header* CreatePacket()
{
	int sizeOfHdr = sizeof(struct _chunk)*3+sizeof(struct _header);
	struct _header* hdr = (struct _header*) malloc(sizeOfHdr);
	struct _chunk* chunks;

	ZeroMemory(hdr, sizeOfHdr);

	hdr->size = sizeOfHdr;
	hdr->chunkCount = 3;
	hdr->version = 0;
	
	chunks = &hdr->chunks[0];
	chunks->type = 0;
	chunks->size = 10;
	strcpy((char*)chunks->data, "123456789");
	
	chunks = &hdr->chunks[1];
	chunks->type = 1;
	chunks->size = 10;
	strcpy((char*)chunks->data, "PEACH6789");
	
	chunks = &hdr->chunks[2];
	chunks->type = 1;
	chunks->size = 10;
	printf("Sizeof(size) == %d", sizeof(chunks->size));
	strcpy((char*)chunks->data, "111111111");

	return hdr;
}

void client(int argc, char** argv)
{
	struct _header* pkt;
	WSADATA wsaData;
	SOCKET ConnectSocket = INVALID_SOCKET;
	struct addrinfo *result = NULL,
		*ptr = NULL,
		hints;
	char *sendbuf = "this is a test";
	char recvbuf[DEFAULT_BUFLEN];
	int iResult;
	int recvbuflen = DEFAULT_BUFLEN;

	// Validate the parameters
	if (argc != 2) {
		printf("usage: %s server-name\n", argv[0]);
		return;
	}

	// Initialize Winsock
	iResult = WSAStartup(MAKEWORD(2,2), &wsaData);
	if (iResult != 0) {
		printf("WSAStartup failed: %d\n", iResult);
		return;
	}

	ZeroMemory( &hints, sizeof(hints) );
	hints.ai_family = AF_INET;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_protocol = IPPROTO_TCP;

	// Resolve the server address and port
	printf("Connecting to port %s:%s\n", argv[1], DEFAULT_PORT);
	iResult = getaddrinfo(argv[1], DEFAULT_PORT, &hints, &result);
	if ( iResult != 0 ) {
		printf("getaddrinfo failed: %d\n", iResult);
		WSACleanup();
		return;
	}

	// Attempt to connect to an address until one succeeds
	for(ptr=result; ptr != NULL ;ptr=ptr->ai_next) {

		// Create a SOCKET for connecting to server
		ConnectSocket = socket(ptr->ai_family, ptr->ai_socktype, 
			ptr->ai_protocol);
		if (ConnectSocket == INVALID_SOCKET) {
			printf("Error at socket(): %ld\n", WSAGetLastError());
			freeaddrinfo(result);
			WSACleanup();
			return;
		}

		// Connect to server.
		iResult = connect( ConnectSocket, ptr->ai_addr, (int)ptr->ai_addrlen);
		if (iResult == SOCKET_ERROR) {
			closesocket(ConnectSocket);
			ConnectSocket = INVALID_SOCKET;
			continue;
		}
		break;
	}

	freeaddrinfo(result);

	if (ConnectSocket == INVALID_SOCKET) {
		printf("Unable to connect to server!\n");
		WSACleanup();
		return;
	}

	// Send an initial buffer
	pkt = CreatePacket();
	iResult = send( ConnectSocket, (char*) pkt, pkt->size, 0 );
	if (iResult == SOCKET_ERROR) {
		printf("send failed: %d\n", WSAGetLastError());
		closesocket(ConnectSocket);
		WSACleanup();
		return;
	}

	printf("Bytes Sent: %ld\n", iResult);

	// shutdown the connection since no more data will be sent
	iResult = shutdown(ConnectSocket, SD_SEND);
	if (iResult == SOCKET_ERROR) {
		printf("shutdown failed: %d\n", WSAGetLastError());
		closesocket(ConnectSocket);
		WSACleanup();
		return;
	}

	// Receive until the peer closes the connection
	do {

		iResult = recv(ConnectSocket, recvbuf, recvbuflen, 0);
		if ( iResult > 0 )
			printf("Bytes received: %d\n", iResult);
		else if ( iResult == 0 )
			printf("Connection closed\n");
		else
			printf("recv failed: %d\n", WSAGetLastError());

	} while( iResult > 0 );

	// cleanup
	closesocket(ConnectSocket);
	WSACleanup();
}

// end
