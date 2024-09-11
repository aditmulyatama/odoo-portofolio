/** @odoo-module **/

import { isMobileOS } from "@web/core/browser/feature_detection";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { url } from "@web/core/utils/urls";
import { isBinarySize } from "@web/core/utils/binary";
import { jsonrpc } from "@web/core/network/rpc_service";
import { FileUploader } from "@web/views/fields/file_handler";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useState, onWillUpdateProps, useRef } from "@odoo/owl";
const { DateTime } = luxon;

export const fileTypeMagicWordMap = {
    "/": "jpg",
    R: "gif",
    i: "png",
    P: "svg+xml",
};

const placeholder = "/web/static/img/placeholder.png";

export function imageCacheKey(value) {
    if (value instanceof DateTime) {
        return value.ts;
    }
    return "";
}

class imageCapture extends Component {
    static template = "CaptureImage";
    static components = { FileUploader };
    static props = {
        ...standardFieldProps,
        enableZoom: { type: Boolean, optional: true },
        zoomDelay: { type: Number, optional: true },
        previewImage: { type: String, optional: true },
        acceptedFileExtensions: { type: String, optional: true },
        width: { type: Number, optional: true },
        height: { type: Number, optional: true },
        reload: { type: Boolean, optional: true },
    };
    static defaultProps = {
        acceptedFileExtensions: "image/*",
        reload: true,
    };

    setup() {
        this.notification = useService("notification");
        this.orm = useService("orm");
        this.isMobile = isMobileOS();
        this.state = useState({
            isValid: true,
            stream: null,
            cameraActive: false, // State to control camera visibility
        });
        this.player = useRef("player");
        this.capture = useRef("capture");
        this.camera = useRef("camera");
        this.rawCacheKey = this.props.record.data.write_date;

        onWillUpdateProps((nextProps) => {
            const { record } = this.props;
            const { record: nextRecord } = nextProps;
            if (record.resId !== nextRecord.resId || nextRecord.mode === "readonly") {
                this.rawCacheKey = nextRecord.data.write_date;
            }
        });
    }

    get sizeStyle() {
        let style = "";
        if (this.props.width) {
            style += `max-width: ${this.props.width}px;`;
        }
        if (this.props.height) {
            style += `max-height: ${this.props.height}px;`;
        }
        return style;
    }

    get hasTooltip() {
        return (
            this.props.enableZoom && this.props.readonly && this.props.record.data[this.props.name]
        );
    }

    getUrl(previewFieldName) {
        if (!this.props.reload && this.lastURL) {
            return this.lastURL;
        }
        if (this.state.isValid && this.props.record.data[this.props.name]) {
            if (isBinarySize(this.props.record.data[this.props.name])) {
                if (!this.rawCacheKey) {
                    this.rawCacheKey = this.props.record.data.write_date;
                }
                this.lastURL = url("/web/image", {
                    model: this.props.record.resModel,
                    id: this.props.record.resId,
                    field: previewFieldName,
                    unique: imageCacheKey(this.rawCacheKey),
                });
            } else {
                const magic =
                    fileTypeMagicWordMap[this.props.record.data[this.props.name][0]] || "png";
                this.lastURL = `data:image/${magic};base64,${this.props.record.data[this.props.name]
                    }`;
            }
            return this.lastURL;
        }
        return placeholder;
    }

    onFileRemove() {
        this.state.isValid = true;
        this.props.record.update({ [this.props.name]: false });
    }

    async onFileUploaded(info) {
        this.state.isValid = true;
        this.rawCacheKey = null;
        this.props.record.update({ [this.props.name]: info.data });
    }

    async OnClickOpenCamera() {
        try {
            this.state.cameraActive = true; // Activate camera
            this.player.el.classList.remove('d-none');
            this.capture.el.classList.remove('d-none');
            this.camera.el.classList.add('d-none');
            this.state.stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
            this.player.el.srcObject = this.state.stream;
        } catch (error) {
            this.notification.add(_t("Camera not detected"), { type: "danger" });
            this.resetCamera();
        }
    }

    stopTracksOnMediaStream(mediaStream) {
        for (const track of mediaStream.getTracks()) {
            track.stop();
        }
    }

    async OnClickCaptureImage() {
        const canvas = document.getElementById('snapshot');
        const context = canvas.getContext('2d');
        const image = document.getElementById('image');
        context.drawImage(this.player.el, 0, 0, 320, 240);
        image.value = context.canvas.toDataURL();
        canvas.classList.remove('d-none');
        this.url = context.canvas.toDataURL();

        // Save the image immediately after capturing
        await this.saveImage();
    }

    async saveImage() {
        const self = this;
        await jsonrpc('/web/dataset/call_kw', {
            model: 'image.capture',
            method: 'action_save_image',
            args: [[], this.url],
            kwargs: {}
        }).then(function (results) {
            self.props.value = results;
            const data = {
                data: results,
                name: "ImageFile.png",
                objectUrl: null,
                size: 106252,
                type: "image/png"
            };
            self.onFileUploaded(data);
        });
        this.resetCamera();
    }

    resetCamera() {
        this.state.cameraActive = false; // Deactivate camera
        this.player.el.classList.add('d-none');
        const snapshot = document.getElementById('snapshot');
        const context = snapshot.getContext('2d');
        context.clearRect(0, 0, snapshot.width, snapshot.height); // Clear the canvas
        snapshot.classList.add('d-none');
        this.capture.el.classList.add('d-none');
        this.camera.el.classList.remove('d-none');
        this.player.el.srcObject = null;
        if (this.state.stream) {
            this.stopTracksOnMediaStream(this.state.stream);
            this.state.stream = null;
        }
        this.url = null; // Reset the URL
    }

    onLoadFailed() {
        this.state.isValid = false;
        this.notification.add(this.env._t("Could not display the selected image"), {
            type: "danger",
        });
    }
}

export const ImageCapture = {
    component: imageCapture,
    displayName: _t("Image"),
    supportedOptions: [
        {
            label: _t("Reload"),
            name: "reload",
            type: "boolean",
            default: true,
        },
        {
            label: _t("Enable zoom"),
            name: "zoom",
            type: "boolean",
        },
        {
            label: _t("Zoom delay"),
            name: "zoom_delay",
            type: "number",
            help: _t("Delay the apparition of the zoomed image with a value in milliseconds"),
        },
        {
            label: _t("Accepted file extensions"),
            name: "accepted_file_extensions",
            type: "string",
        },
        {
            label: _t("Size"),
            name: "size",
            type: "selection",
            choices: [
                { label: _t("Small"), value: "[0,90]" },
                { label: _t("Medium"), value: "[0,180]" },
                { label: _t("Large"), value: "[0,270]" },
            ],
        },
        {
            label: _t("Preview image"),
            name: "preview_image",
            type: "field",
            availableTypes: ["binary"],
        },
    ],
    supportedTypes: ["binary"],
    fieldDependencies: [{ name: "write_date", type: "datetime" }],
    isEmpty: () => false,
    extractProps: ({ attrs, options }) => ({
        enableZoom: options.zoom,
        zoomDelay: options.zoom_delay,
        previewImage: options.preview_image,
        acceptedFileExtensions: options.accepted_file_extensions,
        width: options.size && Boolean(options.size[0]) ? options.size[0] : attrs.width,
        height: options.size && Boolean(options.size[1]) ? options.size[1] : attrs.height,
        reload: "reload" in options ? Boolean(options.reload) : true,
    }),
};

registry.category("fields").add("capture_image", ImageCapture);