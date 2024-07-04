from ffmpeg import FFmpeg, Progress

# apt install -y python-ffmpeg if you get errors here.

def main():
    ffmpeg = (
        FFmpeg()
        .option("y")
        .input("music/")
        .output(
            "o",
            {"codec:v": "libx264"},
            vf="scale=1280:-1",
            preset="veryslow",
            crf=24,
        )
    )

    ffmpeg.execute()


if __name__ == "__main__":
    main()
