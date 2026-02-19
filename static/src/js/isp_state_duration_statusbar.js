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

    _getSurveyRunningDuration(data) {
        const now = new Date();

        const draftAt = this._toDate(data.state_draft_date) || this._toDate(data.create_date);
        const doneAt = this._toDate(data.state_done_date);
        const workAt = this._toDate(data.state_work_order_date);
        const workStopAt = this._toDate(data.state_work_order_stop_date);

        if (data.state === "draft" && draftAt) {
            return { state: "draft", sec: Math.floor((now - draftAt) / 1000) };
        }
        if (data.state === "done" && doneAt) {
            return { state: "done", sec: Math.floor((now - doneAt) / 1000) };
        }
        if (data.state === "work_order" && workAt && !workStopAt) {
            return { state: "work_order", sec: Math.floor((now - workAt) / 1000) };
        }
        return null;
    }

    _getSurveyItems(items, data) {
        const fixedDraftDone = data.dur_draft_to_done_display || "";
        const fixedDoneWork = data.dur_done_to_work_display || "";
        const fixedWorkOrderActive = data.dur_work_order_active_display || "";
        const workAt = this._toDate(data.state_work_order_date);
        const workStopAt = this._toDate(data.state_work_order_stop_date);
        const running = this._getSurveyRunningDuration(data);

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
                } else if (fixedWorkOrderActive) {
                    extra = fixedWorkOrderActive;
                } else if (workAt && workStopAt && workStopAt > workAt) {
                    extra = this._formatSeconds(Math.floor((workStopAt - workAt) / 1000));
                }
            }

            const baseLabel = it.label;
            const label = extra ? `${baseLabel} (${extra})` : baseLabel;
            return { ...it, label, baseLabel, extraDuration: extra };
        });
    }

    _getWorkStateDateMap(data) {
        const workOrderStartedAt =
            this._toDate(data.work_state_work_order_date) ||
            this._toDate(data.state_work_order_date) ||
            this._toDate(data.create_date);
        return {
            work_order: workOrderStartedAt,
            sell_confirm: this._toDate(data.work_state_sell_confirm_date),
            marketing_confirm: this._toDate(data.work_state_marketing_confirm_date),
            marketing_revert: this._toDate(data.work_state_marketing_revert_date),
            legal_confirm: this._toDate(data.work_state_legal_confirm_date),
            legal_revert: this._toDate(data.work_state_legal_revert_date),
        };
    }

    _getWorkRunningDuration(data, stateDates) {
        const state = data.work_state;
        const startedAt = stateDates[state];
        if (!startedAt) {
            return null;
        }
        const now = new Date();
        return { state, sec: Math.floor((now - startedAt) / 1000) };
    }

    _getNextStateDate(currentDate, stateDates) {
        if (!currentDate) {
            return null;
        }
        let nextDate = null;
        for (const dt of Object.values(stateDates)) {
            if (!dt || dt <= currentDate) {
                continue;
            }
            if (!nextDate || dt < nextDate) {
                nextDate = dt;
            }
        }
        return nextDate;
    }

    _getWorkItems(items, data) {
        const stateDates = this._getWorkStateDateMap(data);
        const running = this._getWorkRunningDuration(data, stateDates);

        return items.map((it) => {
            let extra = "";
            const stateValue = it.value;

            const startedAt = stateDates[stateValue];
            if (data.work_state === stateValue && running?.state === stateValue) {
                extra = this._formatSeconds(Math.max(0, running.sec));
            } else if (startedAt) {
                const nextAt = this._getNextStateDate(startedAt, stateDates);
                if (nextAt) {
                    const sec = Math.floor((nextAt - startedAt) / 1000);
                    extra = this._formatSeconds(Math.max(0, sec));
                }
            }

            const baseLabel = it.label;
            const label = extra ? `${baseLabel} (${extra})` : baseLabel;
            return { ...it, label, baseLabel, extraDuration: extra };
        });
    }

    getAllItems() {
        // trigger rerender
        this._tick.n;

        const items = super.getAllItems();
        const data = this.props.record.data;
        if (this.props.name === "work_state") {
            return this._getWorkItems(items, data);
        }
        return this._getSurveyItems(items, data);
    }
}

registry.category("fields").add("isp_state_duration_statusbar", {
    ...statusBarField,
    component: IspStateDurationStatusBar,
    additionalClasses: [...(statusBarField.additionalClasses || []), "o_field_statusbar"],
});
