
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <netinet/ip.h>

void main(int argc, char** argv)
{
  int s, childFd;
  struct sockaddr_in myAddr;
  struct sockaddr addr;
  socklen_t addrlen = sizeof(addr);

  printf("\n");  
  printf("] unixcrash -- Part of the Peach Unittests\n");
  printf("] copyright (c) Michael Eddington\n\n");
  
  memset(&myAddr, 0, sizeof(struct sockaddr_in));
  myAddr.sin_family = AF_INET;
  myAddr.sin_port = htons(4242);
  myAddr.sin_addr.s_addr = INADDR_ANY;

  s = socket(PF_INET, SOCK_STREAM, 0);
  if(s == -1)
  {
    printf("socket() failed, exiting\n");
    return;
  }
  
  if(bind(s, (struct sockaddr*)&myAddr, sizeof(struct sockaddr_in)) == -1)
  {
    printf("bind() failed, exiting\n");
    close(s);
    return;
  }
  
  printf("Listening for connections...");
  fflush(stdout);
  while(listen(s, 1) != -1)
  {
    char buff[5];
    
    memset(&addr, 0, sizeof(addr));
    addrlen = sizeof(addr);
    
    childFd = accept(s, &addr, &addrlen);
    if(childFd == -1)
    {
      printf("error\naccept() failed, exiting\n");
      close(s);
      return;
    }
    
    printf("got one!\n");
    
    
    sleep(2);
    
    // Do crazy things here
    fcntl(childFd, F_SETFL, O_NONBLOCK);
    int count = recv(childFd, buff, 1024, MSG_DONTWAIT);
    close(childFd);
    
    printf("recv: %d\n\n", count);
    
    printf("Listening for connections...");
    fflush(stdout);
  }
  
  printf("failed, exiting\n");
  close(s);
}

// end //
