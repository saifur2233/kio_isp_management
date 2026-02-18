/** @odoo-module **/

import { registry } from "@web/core/registry";
import { StatusBarField, statusBarField } from "@web/views/fields/statusbar/statusbar_field";
import { useState, onWillUnmount } from "@odoo/owl";

export class IspStateDurationStatusBar extends StatusBarField {
    static template = "kio_isp_management.IspStateDurationStatusBar";

    setup() {
        super.setup();
        this._tick = useState({ n: 0 });

        // refresh label every 30 seconds
        this._timer = setInterval(() => {
            this._tick.n++;
        }, 30000);

        onWillUnmount(() => clearInterval(this._timer));
    }

    _formatSeconds(sec) {
        sec = parseInt(sec || 0, 10);
        if (sec <= 0) return "0m";

        const minutes = Math.floor(sec / 60);
        const days = Math.floor(minutes / (60 * 24));
        const hours = Math.floor(minutes / 60) % 24;
        const mins = minutes % 60;

        const parts = [];
        if (days) parts.push(`${days}d`);
        if (hours) parts.push(`${hours}h`);
        if (mins || parts.length === 0) parts.push(`${mins}m`);
        return parts.join(" ");
    }

    _toDate(val) {
        if (!val) return null;
        if (val instanceof Date) return val;
        if (typeof val === "string") {
            // "YYYY-MM-DD HH:MM:SS" -> "YYYY-MM-DDTHH:MM:SS"
            return new Date(val.replace(" ", "T"));
        }
        if (typeof val.toJSDate === "function") {
            return val.toJSDate();
        }
        const parsed = new Date(val);
        return Number.isNaN(parsed.getTime()) ? null : parsed;
    }

    _getRunningDuration(data) {
        const now = new Date();

        const draftAt = this._toDate(data.state_draft_date) || this._toDate(data.create_date);
        const doneAt = this._toDate(data.state_done_date);
        const workAt = this._toDate(data.state_work_order_date);

        if (data.state === "draft" && draftAt) {
            return { state: "draft", sec: Math.floor((now - draftAt) / 1000) };
        }
        if (data.state === "done" && doneAt) {
            return { state: "done", sec: Math.floor((now - doneAt) / 1000) };
        }
        if (data.state === "work_order" && workAt) {
            return { state: "work_order", sec: Math.floor((now - workAt) / 1000) };
        }
        return null;
    }

    getAllItems() {
        // trigger rerender
        this._tick.n;

        const items = super.getAllItems();
        const data = this.props.record.data;

        const fixedDraftDone = data.dur_draft_to_done_display || "";
        const fixedDoneWork = data.dur_done_to_work_display || "";
        const running = this._getRunningDuration(data);

        return items.map((it) => {
            let extra = "";

            if (it.value === "draft") {
                if (data.state === "draft" && running?.state === "draft") {
                    extra = this._formatSeconds(running.sec);
                } else if (fixedDraftDone) {
                    extra = fixedDraftDone;
                }
            }

            if (it.value === "done") {
                if (data.state === "done" && running?.state === "done") {
                    extra = this._formatSeconds(running.sec);
                } else if (fixedDoneWork) {
                    extra = fixedDoneWork;
                }
            }

            if (it.value === "work_order") {
                if (data.state === "work_order" && running?.state === "work_order") {
                    extra = this._formatSeconds(running.sec);
                }
            }

            const baseLabel = it.label;
            const label = extra ? `${baseLabel} (${extra})` : baseLabel;
            return { ...it, label, baseLabel, extraDuration: extra };
        });
    }
}

registry.category("fields").add("isp_state_duration_statusbar", {
    ...statusBarField,
    component: IspStateDurationStatusBar,
    additionalClasses: [...(statusBarField.additionalClasses || []), "o_field_statusbar"],
});
