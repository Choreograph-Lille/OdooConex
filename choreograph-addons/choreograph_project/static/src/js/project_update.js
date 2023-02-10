/** @odoo-module **/

import { KanbanController } from "@web/views/kanban/kanban_controller";
import { kanbanView } from '@web/views/kanban/kanban_view';
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";

export class KanbanProjectUpdate extends KanbanController {
    async setup() {
        super.setup();
        this.orm = useService('orm');
    }
    async onRedeliveryStudies() {
        await this.orm.call(this.props.resModel, 'js_redelivery', [this.props.context.active_id, 'studies'], {});
    }
    async onRedeliveryProd() {
        await this.orm.call(this.props.resModel, 'js_redelivery', [this.props.context.active_id, 'prod'], {});
    }
};

registry.category('views').add('project_update_redelivery', {
    ...kanbanView,
    Controller: KanbanProjectUpdate,
    buttonTemplate: 'choreograph_project.buttons',
}); 
