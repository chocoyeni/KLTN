<?php

require('../../config.php');
require_login();

global $PAGE, $OUTPUT;

$PAGE->set_url('/local/ednet_import/generate.php');
$PAGE->set_context(context_system::instance());
$PAGE->set_title('Generated Quiz');

$PAGE->requires->css(
    new moodle_url(
        '/local/ednet_import/style.css',
        ['v' => time()]
    )
);

$easy = (int)$_POST['easy'];
$medium = (int)$_POST['medium'];
$hard = (int)$_POST['hard'];

$data = [
    'easy' => $easy,
    'medium' => $medium,
    'hard' => $hard
];

$jsonData = json_encode($data);

$url = 'http://192.168.74.1:8000/generate_quiz';

$ch = curl_init($url);

curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

curl_setopt($ch, CURLOPT_POST, true);

curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json'
]);

curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonData);

$response = curl_exec($ch);

# =========================
# HTTP CODE
# =========================

$httpcode = curl_getinfo(
    $ch,
    CURLINFO_HTTP_CODE
);

# =========================
# CURL ERROR
# =========================

if(curl_errno($ch)) {

    echo $OUTPUT->header();

    ?>

    <div class="adaptive-container">

        <div class="adaptive-card">

            <h1>API CONNECTION ERROR</h1>

            <div class="error-box">

                <?php echo curl_error($ch); ?>

            </div>

        </div>

    </div>

    <?php

    echo $OUTPUT->footer();

    curl_close($ch);

    exit;
}

curl_close($ch);

# =========================
# HTTP ERROR
# =========================

if($httpcode != 200){

    echo $OUTPUT->header();

    ?>

    <div class="adaptive-container">

        <div class="adaptive-card">

            <h1>API ERROR</h1>

            <div class="error-box">

                HTTP CODE:
                <?php echo $httpcode; ?>

            </div>

        </div>

    </div>

    <?php

    echo $OUTPUT->footer();

    exit;
}

# =========================
# JSON DECODE
# =========================

$result = json_decode($response, true);

# =========================
# INVALID JSON
# =========================

if(!$result){

    echo $OUTPUT->header();

    ?>

    <div class="adaptive-container">

        <div class="adaptive-card">

            <h1>INVALID JSON RESPONSE</h1>

        </div>

    </div>

    <?php

    echo $OUTPUT->footer();

    exit;
}

# =========================
# SERVER ERROR
# =========================

if(isset($result['detail'])){

    echo $OUTPUT->header();

    ?>

    <div class="adaptive-container">

        <div class="adaptive-card">

            <h1>SERVER ERROR</h1>

            <div class="error-box">

                <?php echo $result['detail']; ?>

            </div>

        </div>

    </div>

    <?php

    echo $OUTPUT->footer();

    exit;
}

$questions = $result['questions'];
$total = $result['total'];

# =========================
# EMPTY RESULT
# =========================

if($total <= 0){

    echo $OUTPUT->header();

    ?>

    <div class="adaptive-container">

        <div class="adaptive-card">

            <h1>NO QUESTIONS GENERATED</h1>

        </div>

    </div>

    <?php

    echo $OUTPUT->footer();

    exit;
}

echo $OUTPUT->header();

# =========================
# WARNINGS
# =========================

if(
    isset($result['warnings'])
    &&
    count($result['warnings']) > 0
){

    foreach($result['warnings'] as $warning){

        ?>

        <div class="warning-box">

            WARNING:
            <?php echo $warning; ?>

        </div>

        <?php
    }
}

?>

<div class="adaptive-container">

    <div class="adaptive-card">

        <h1>Generated Adaptive Quiz</h1>

        <p class="subtitle">

            Total Questions:
            <?php echo $total; ?>

        </p>

        <div class="button-row">

            <form
                action="export.php"
                method="POST"
                class="button-form"
            >

                <input
                    type="hidden"
                    name="questions"
                    value='<?php echo json_encode($questions); ?>'
                >

                <button
                    type="submit"
                    class="generate-btn full-btn"
                >

                    Export CSV

                </button>

            </form>

            <a
                href="index.php"
                class="generate-btn full-btn"
            >

                Generate Another Quiz

            </a>

        </div>

        <div class="question-grid">

            <?php foreach($questions as $q): ?>

                <div class="
                    question-box
                    <?php echo strtolower($q['difficulty']); ?>
                ">

                    <div class="question-id">

                        Question ID:
                        <?php echo $q['question_id']; ?>

                    </div>

                    <br>

                    <div class="
                        difficulty-badge
                        difficulty-<?php echo strtolower($q['difficulty']); ?>
                    ">

                        <?php echo $q['difficulty']; ?>

                    </div>

                </div>

            <?php endforeach; ?>

        </div>

    </div>

</div>

<?php

echo $OUTPUT->footer();

?>