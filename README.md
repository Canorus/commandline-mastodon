# commandline-mastodon

Basic code to test sending toot/stream timeline from commandline. Requires python3.

`quit` terminates code.

caveat: login credentials(especially access token) are saved to local file as `cred.json`. Be **very** careful not to share this file anywhere online.

## Streaming timeline

running `streaming.py` file will stream local timelines. Modify line 10 to `https://whatever_your_instance_address/api/v1/streaming/user` to stream user home timeline.

`ctrl`+`c` terminates streaming.

## Todo

- [x] line break
- [x] Timeline streaming on commandline
- [ ] Integrated home-local timeline
- [ ] strip off html tags
- [ ] show images to commandline, perhaps?
- [ ] posting with CW or NSFW attention
- [ ] posting image from clipboard