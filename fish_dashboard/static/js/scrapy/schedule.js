$("#schedule_form").bootstrapValidator({
    message: "This value is not valid.",
    feedbackIcons: {
        valid: 'glyphicon glyphicon-ok',
        invalid: 'glyphicon glyphicon-remove',
        validating: 'glyphicon glyphicon-refresh'
    },
    fields: {
        project_name: {
            message: 'Project Name validate failure!',
            validators: {
                notEmpty: {
                    message: 'Project Name must is not empty!'
                }
            }
        },
        spider_name: {
            message: 'Spider Name validate failure!',
            validators: {
                notEmpty: {
                    message: 'Spider Name must is not empty!'
                }
            }
        }
    }
});