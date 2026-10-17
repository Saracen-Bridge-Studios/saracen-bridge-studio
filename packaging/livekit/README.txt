LiveKit server 1.13.10 (Apache-2.0, see LICENSE-livekit.txt and NOTICE-livekit.txt) for the Room's voice huddles and
meetings when a Studio hosts its own productions (1.1.0). Built from LiveKit's published source for that release
(Go module github.com/livekit/livekit-server@v1.13.10, commit e5655ac2) with:
    CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build -trimpath -ldflags "-s -w" ./cmd/server
The exe is not kept in git (see .gitignore); the build copies it here.
4584496c965273e0c565acdcb242c3cad9a5a95ae5a3dba017ec58d356bee084  packaging/livekit/livekit-server.exe
