
/* this is only needed for compatibility with the old talloc */
typedef void TALLOC_CTX;
/* used to hold an arbitrary blob of data */
/* CAB data blocks are <= 32768 bytes in uncompressed form. Uncompressed
 * blocks have zero growth. MSZIP guarantees that it won't grow above
 * uncompressed size by more than 12 bytes. LZX guarantees it won't grow
 * more than 6144 bytes.
 */
#define CAB_BLOCKMAX (32768)
#define CAB_INPUTMAX (CAB_BLOCKMAX+6144)
#define ZIPWSIZE 	0x8000  /* window size */

#define uint8_t unsigned char 
#define uint32_t unsigned int
#define uint16_t unsigned short

#define int8_t char 
#define int32_t int
#define int16_t short

typedef struct datablob {
	uint8_t *data;
	size_t length;
} DATA_BLOB;

struct decomp_state;
struct decomp_state * ZIPdecomp_state(TALLOC_CTX *mem_ctx);

#define DECR_OK           (0)
#define DECR_DATAFORMAT   (1)
#define DECR_ILLEGALDATA  (2)
#define DECR_NOMEMORY     (3)
#define DECR_CHECKSUM     (4)
#define DECR_INPUT        (5)
#define DECR_OUTPUT       (6)

int ZIPdecompress(struct decomp_state *decomp_state, DATA_BLOB *inbuf, DATA_BLOB *outbuf);
