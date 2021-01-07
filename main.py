import cv2
import mido
import time
import numpy as np


def main():
    #40
    #img = cv2.imread("Van Gogh/Saint Remy/Half Figure of an Angel after Rembrandt.jpg")
    #img = cv2.imread("Van Gogh/Saint Remy/Irises.jpg")
    #img = cv2.imread("Van Gogh/Paris/Vase with Asters and Phlox.jpg")
    #80
    #img = cv2.imread("Van Gogh/Paris/The Kingfisher.jpg")
    img = cv2.imread("Van Gogh/Paris/The Hill of Montmartre with Quarry.jpg")
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    scale_percent = 25
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)

    img = cv2.resize(img, dim)
    hsv_img = cv2.resize(hsv_img, dim)

    #cv2.imshow("OG", img)
    #cv2.imshow("HSV", hsv_img)

    out_port = mido.open_output("loopMIDI Port 2")

    step_size = 80
    for y in range(0, height, step_size):
        for x in range(0, width, step_size):
            sub_img = hsv_img[y:y+step_size, x:x+step_size]
            mean_hsv = np.round(np.mean(sub_img.reshape(-1, 3), axis=0)).astype(np.int)

            hsv_img[y:y+step_size, x:x+step_size] = img[y:y+step_size, x:x+step_size]
            cv2.imshow("HSV", hsv_img)
            cv2.waitKey(1)

            hue = scale_between_range(mean_hsv[0], 0, 179, 0, 127)
            saturation = scale_between_range(mean_hsv[1], 0, 255, 0, 127)
            intensity = scale_between_range(mean_hsv[2], 0, 255, 0, 127)

            hue_note = mido.Message("note_on", note=hue, velocity=intensity)
            sat_note = mido.Message("note_on", note=saturation, velocity=intensity)
            int_note = mido.Message("note_on", note=intensity, velocity=intensity)
            out_port.send(hue_note)
            out_port.send(sat_note)
            out_port.send(int_note)
            time.sleep(scale_between_range(hue + saturation + intensity, 0, 127*3, 1, 5))
            hue_note = mido.Message("note_off", note=hue, velocity=intensity)
            sat_note = mido.Message("note_off", note=saturation, velocity=intensity)
            int_note = mido.Message("note_off", note=intensity, velocity=intensity)
            out_port.send(hue_note)
            out_port.send(sat_note)
            out_port.send(int_note)

    cv2.destroyAllWindows()


def scale_between_range(value, in_min, in_max, out_min, out_max):
    scaled = round(out_min + (value - in_min) * ((out_max - out_min) / (in_max - in_min)))
    if scaled > out_max:
        return out_max
    if scaled < out_min:
        return out_min
    return scaled


if __name__ == "__main__":
    main()
