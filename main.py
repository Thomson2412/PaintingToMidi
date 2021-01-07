import cv2
import mido
import time
import threading
import numpy as np


def main():
    # img = cv2.imread("Van Gogh/Saint Remy/Half Figure of an Angel after Rembrandt.jpg")
    img = cv2.imread("Van Gogh/Saint Remy/Irises.jpg")
    # img = cv2.imread("Van Gogh/Paris/Vase with Asters and Phlox.jpg")
    # img = cv2.imread("Van Gogh/Paris/The Kingfisher.jpg")
    # img = cv2.imread("Van Gogh/Paris/The Hill of Montmartre with Quarry.jpg")
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    scale_percent = 25
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)

    img = cv2.resize(img, dim)
    hsv_img = cv2.resize(hsv_img, dim)

    # cv2.imshow("OG", img)
    # cv2.imshow("HSV", hsv_img)

    in_port = mido.open_input("loopMIDI Port 1")
    out_port = mido.open_output("loopMIDI Port 2")

    step_size = 80
    x_list = range(0, width, step_size)
    y_list = range(0, height, step_size)
    x_index = 0
    y_index = 0

    clock_count = 0
    for msg in in_port:
        if clock_count == 192 or msg.type == "start":
            x = x_list[x_index]
            y = y_list[y_index]

            sub_img = hsv_img[y:y + step_size, x:x + step_size]
            mean_hsv = np.round(np.mean(sub_img.reshape(-1, 3), axis=0)).astype(np.int)

            hue = scale_between_range(mean_hsv[0], 0, 179, 1, 127)
            saturation = scale_between_range(mean_hsv[1], 0, 255, 1, 127)
            intensity = scale_between_range(mean_hsv[2], 0, 255, 1, 127)

            note_duration = scale_between_range(hue + saturation + intensity, 3, 127 *3, 2, 6)
            make_sound(hue, saturation, intensity, intensity, note_duration, out_port)

            hsv_img[y:y + step_size, x:x + step_size] = img[y:y + step_size, x:x + step_size]
            cv2.imshow("HSV", hsv_img)
            cv2.waitKey(1)

            x_index += 1
            if x_index == len(x_list):
                x_index = 0
                y_index += 1
                if y_index == len(y_list):
                    break

            clock_count = 0

        if msg.type == "clock":
            clock_count += 1

    cv2.destroyAllWindows()


def make_sound(note_0, note_1, note_2, vel, dur, out_port):
    hue_note = mido.Message("note_on", note=note_0, velocity=vel)
    sat_note = mido.Message("note_on", note=note_1, velocity=vel)
    int_note = mido.Message("note_on", note=note_2, velocity=vel)
    out_port.send(hue_note)
    out_port.send(sat_note)
    out_port.send(int_note)

    hue_note = mido.Message("note_off", note=note_0, velocity=vel)
    sat_note = mido.Message("note_off", note=note_1, velocity=vel)
    int_note = mido.Message("note_off", note=note_2, velocity=vel)
    threading.Timer(dur, lambda: out_port.send(hue_note)).start()
    threading.Timer(dur, lambda: out_port.send(sat_note)).start()
    threading.Timer(dur, lambda: out_port.send(int_note)).start()


def scale_between_range(value, in_min, in_max, out_min, out_max):
    scaled = round(out_min + (value - in_min) * ((out_max - out_min) / (in_max - in_min)))
    if scaled > out_max:
        return out_max
    if scaled < out_min:
        return out_min
    return scaled


if __name__ == "__main__":
    main()
