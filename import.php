<?php

require('../../config.php');
require_login();

global $PAGE, $OUTPUT;

$PAGE->set_url('/local/ednet_import/index.php');
$PAGE->set_context(context_system::instance());
$PAGE->set_title('Adaptive Quiz Generator');

$PAGE->requires->css(
    new moodle_url('/local/ednet_import/style.css')
);

echo $OUTPUT->header();

?>

<div class="adaptive-container">

    <div class="adaptive-card">

        <h1>Adaptive Quiz Generator</h1>

        <p class="subtitle">
            Generate quizzes using LNIRT
            and machine learning clustering.
        </p>

        <form
            method="post"
            action="generate.php"
            onsubmit="showLoading()"
        >

            <div class="input-group">

                <label>Easy Questions</label>

                <input
                    type="number"
                    name="easy"
                    value="5"
                    min="0"
                >

            </div>

            <div class="input-group">

                <label>Medium Questions</label>

                <input
                    type="number"
                    name="medium"
                    value="5"
                    min="0"
                >

            </div>

            <div class="input-group">

                <label>Hard Questions</label>

                <input
                    type="number"
                    name="hard"
                    value="5"
                    min="0"
                >

            </div>

            <button
                type="submit"
                class="generate-btn"
            >
                Generate Adaptive Quiz
            </button>

        </form>

    </div>

</div>

<div id="loading-box" style="display:none;">

    <div class="loading-card">

        <h2>
            Training Adaptive Model...
        </h2>

        <p>
            Please wait while the system
            retrains LNIRT and generates
            a personalized quiz.
        </p>

    </div>

</div>

<script>

function showLoading() {

    document.getElementById(
        "loading-box"
    ).style.display = "flex";

}

</script>

<?php

echo $OUTPUT->footer();