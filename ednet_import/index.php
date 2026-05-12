<?php

require('../../config.php');
require_login();

global $PAGE, $OUTPUT;

$PAGE->set_url('/local/ednet_import/index.php');
$PAGE->set_context(context_system::instance());
$PAGE->set_title('Adaptive Quiz Generator');

$PAGE->requires->css(
    new moodle_url(
        '/local/ednet_import/style.css',
        ['v' => time()]
    )
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

            <div class="difficulty-grid">

                <div class="difficulty-card easy-card">

                    <div class="difficulty-icon">
                        
                    </div>

                    <div class="difficulty-title">
                        Easy
                    </div>

                    <div class="difficulty-desc">
                        Basic and introductory questions
                    </div>

                    <input
                        type="number"
                        name="easy"
                        value="5"
                        min="0"
                    >

                </div>

                <div class="difficulty-card medium-card">

                    <div class="difficulty-icon">
                        
                    </div>

                    <div class="difficulty-title">
                        Medium
                    </div>

                    <div class="difficulty-desc">
                        Moderate difficulty questions
                    </div>

                    <input
                        type="number"
                        name="medium"
                        value="5"
                        min="0"
                    >

                </div>

                <div class="difficulty-card hard-card">

                    <div class="difficulty-icon">
                        
                    </div>

                    <div class="difficulty-title">
                        Hard
                    </div>

                    <div class="difficulty-desc">
                        Advanced and challenging questions
                    </div>

                    <input
                        type="number"
                        name="hard"
                        value="5"
                        min="0"
                    >

                </div>

            </div>

            <div class="generate-wrapper">

                <button
                    type="submit"
                    class="generate-btn main-generate-btn"
                >

                     Generate Adaptive Quiz

                </button>

            </div>

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

?>
