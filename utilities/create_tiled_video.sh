#!/bin/bash

# Usage: ./create_tiled_video.sh <folder_path> <rows> <cols> <output_file>
# Example: ./create_tiled_video.sh /path/to/videos 5 5 tiled_output.mp4

FOLDER_PATH="$1"
ROWS="$2"
COLS="$3"
OUTPUT_FILE="$4"

# Ensure folder exists
if [ ! -d "$FOLDER_PATH" ]; then
    echo "❌ Error: Folder '$FOLDER_PATH' does not exist."
    exit 1
fi

# Get all MP4 files from the folder
VIDEO_FILES=($(ls "$FOLDER_PATH"/*.mp4 2>/dev/null | sort))
NUM_VIDEOS=${#VIDEO_FILES[@]}

# Ensure enough videos are available
if [ "$NUM_VIDEOS" -lt "$(($ROWS * $COLS))" ]; then
    echo "⚠️ Not enough videos ($NUM_VIDEOS) to fill a ${ROWS}x${COLS} grid."
    exit 1
fi

# Generate FFmpeg input arguments
INPUT_ARGS=""
FILTER_COMPLEX=""
COUNT=0

for FILE in "${VIDEO_FILES[@]:0:$((ROWS * COLS))}"; do
    INPUT_ARGS+="-i \"$FILE\" "
    FILTER_COMPLEX+="[$COUNT:v] setpts=PTS-STARTPTS [v$COUNT]; "
    COUNT=$((COUNT + 1))
done

# Append xstack filter for tiling videos correctly
FILTER_COMPLEX+="[v0][v1][v2][v3][v4][v5][v6][v7][v8][v9][v10][v11][v12][v13][v14][v15][v16][v17][v18][v19][v20][v21][v22][v23][v24]xstack=inputs=25:layout=0_0|640_0|1280_0|1920_0|2560_0|0_480|640_480|1280_480|1920_480|2560_480|0_960|640_960|1280_960|1920_960|2560_960|0_1440|640_1440|1280_1440|1920_1440|2560_1440|0_1920|640_1920|1280_1920|1920_1920|2560_1920[out]"

# Construct full FFmpeg command
CMD="ffmpeg $INPUT_ARGS -filter_complex \"${FILTER_COMPLEX}\" -map \"[out]\" -c:v libx264 -crf 23 -preset fast \"$OUTPUT_FILE\""

# Execute the command
eval $CMD
