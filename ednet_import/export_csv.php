
<?php

require('../../config.php');
require_login();

$questions = json_decode(
    $_POST['questions'],
    true
);

header('Content-Type: text/csv');
header(
    'Content-Disposition: attachment; filename="adaptive_quiz.csv"'
);

$output = fopen('php://output', 'w');

fputcsv($output, [

    'Question ID',
    'Difficulty',
    'Beta',
    'Alpha',
    'Lambda',
    'Phi'

]);

foreach($questions as $q) {

    fputcsv($output, [

        $q['question_id'],
        $q['difficulty'],

        $q['beta'],
        $q['alpha'],
        $q['lambda'],
        $q['phi']

    ]);
}

fclose($output);

exit;

