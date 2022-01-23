

<?php

	$aws_access_key_id='ASIAXBQ2N3L47ACMKZAX';

	$aws_secret_access_key='UJ0Wz0yT+fXKP7yEuXU82A3+FBkQY0x9wwqu758g';

	$aws_session_token='FwoGZXIvYXdzEEwaDF9Ye1L4h10rRXsq/yK8AeUd9mPvRlBM+4mRh4tbjyIY/5d6m9BWjC/Mkqs6jdzxt9mZOj2wL9KaKaaRXS2EuSeEzLGJsHE0eBk/cb9RZdW70YlZVfUHbdOU5pYFtpVfx2hNLDsP3XGYC65p1w+4HySquaw2QKhTCl4wX2Ed1iM+8Tri/g92YXnyxNGv5V9IVM1skSuZl+SOynzhC3dgIjQ2NUAtMkwpHA5NZhTVbblsV6qoymwlFer6dHi0fH0JrudRsN7LlfX2wSEKKLPMto8GMi3Wnji9OVq2rO5QDsBLlF7GNZ9quFaVzjOb920t0gzmO1F7PWd6zr6tRIBAa1I=';

	$lambda_func='utadtube';
	$payload='{"queryStringParameters": {';

	foreach ($_GET as $key => $value) {

		$payload .= '"' . $key . '":"' . $value .'",';

	}

	$payload=substr($payload, 0, -1);

	$payload.='}}';

	$cmd=' AWS_ACCESS_KEY_ID='. $aws_access_key_id .

	     ' AWS_SECRET_ACCESS_KEY='. $aws_secret_access_key .

             ' AWS_SESSION_TOKEN='. $aws_session_token . ' aws lambda invoke --function-name --region us-east-1 '. $lambda_func . ' --payload \'' . $payload . '\' /tmp/resp.json 2>&1';

	exec( $cmd,$result,$result2);

	header('Access-Control-Allow-Origin: *');

	$result=file_get_contents("/tmp/resp.json");

	$json=json_decode($result,true);

    echo json_encode($json['body']);
?>



