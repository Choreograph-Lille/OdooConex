/** @odoo-module */

import { ProjectTaskKanbanRenderer } from '@project/views/project_task_kanban/project_task_kanban_renderer';
import { patch } from "@web/core/utils/patch";

patch(ProjectTaskKanbanRenderer.prototype, "project_task_kanban_renderer",{
    get canResequenceGroups(){
        return false
    },
})