# Helpers for the four-camera adapter. Sourced by the other scripts in pi/.
#
# The adapter is switched over I2C (bus 10, device 0x24, register 0x24).
# Writing 0x02, 0x12, 0x22 or 0x32 selects camera 0, 1, 2 or 3.
#
# Each camera sits at a different distance from the part, so each has its own
# fixed lens position. CAMERA_LENS lists them for cameras 0 to 3 (faces 1 to 4).
# Set CAMERA_LENS=auto to use autofocus instead.

I2C_BUS="${I2C_BUS:-10}"
CAMERA_LENS="${CAMERA_LENS:-8 7 7 8}"

# select_camera <0-3>
select_camera() {
    i2cset -y "$I2C_BUS" 0x24 0x24 "0x${1}2"
}

# lens_for_camera <0-3>  -> prints the configured lens position, or nothing for autofocus
lens_for_camera() {
    [ "$CAMERA_LENS" = "auto" ] && return 0
    local positions=($CAMERA_LENS)
    echo "${positions[$1]}"
}

# capture <output.jpg> [lens_position]
# With a lens position the focus is set manually; without one, autofocus is used.
capture() {
    local out="$1" lens="${2:-}"
    if [ -n "$lens" ]; then
        libcamera-still -o "$out" --autofocus-mode manual --lens-position "$lens"
    else
        libcamera-still -o "$out" --autofocus-on-capture
    fi
}
