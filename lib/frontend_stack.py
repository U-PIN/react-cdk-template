import json

import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (
  Stack,
  CfnOutput,
  aws_ssm as ssm,
  aws_s3 as s3,
  aws_certificatemanager as acm,
  aws_cloudfront as cloudfront,
  aws_route53 as route53,
  aws_route53_targets as targets,
)

config_params = json.load(open("config.params.json", "r"))
namespace = config_params["Namespace"]


class FrontendStack(Stack):

  @property
  def s3_bucket_name(self):
    return self._s3_bucket_name

  @property
  def app_url(self):
    return self._app_url

  def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    cloudfront_alias_cert_arn = ssm.StringParameter.value_for_string_parameter(self, namespace + "CloudFrontAliasCertArn")
    cloudfront_domain_name = ssm.StringParameter.value_for_string_parameter(self, namespace + "CloudFrontDomainName")
    hosted_zone_id = ssm.StringParameter.value_for_string_parameter(self, namespace + "HostedZoneId")    
    hosted_zone_name = ssm.StringParameter.value_for_string_parameter(self, namespace + "HostedZoneName")

    bucket = s3.Bucket(self, "ReactWebAppHostingBucket", )
    bucket.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

    certificate = acm.Certificate.from_certificate_arn(self, "Certificate", certificate_arn=cloudfront_alias_cert_arn)

    cloudfront_oai = cloudfront.OriginAccessIdentity(self, "MyCfnCloudFrontOriginAccessIdentity")
    cloudfront_distribution = cloudfront.CloudFrontWebDistribution(self, "ReactWebbAppDistribution",
      comment="CloudFront Distribution for {}".format(namespace.replace("/", "")),
      default_root_object="index.html",
      viewer_certificate=cloudfront.ViewerCertificate.from_acm_certificate(certificate,
        aliases=[cloudfront_domain_name],
      ),
      origin_configs=[
        cloudfront.SourceConfiguration(
          s3_origin_source=cloudfront.S3OriginConfig(
            s3_bucket_source=bucket,
            origin_access_identity=cloudfront_oai
          ),
          behaviors=[cloudfront.Behavior(is_default_behavior=True)]
        )
      ],
      error_configurations=[
        cloudfront.CfnDistribution.CustomErrorResponseProperty(
          error_code=404,
          error_caching_min_ttl=0,
          response_code=200,
          response_page_path="/index.html"
        ) 
      ]
    )
    bucket.grant_read(cloudfront_oai.grant_principal)

    zone = route53.HostedZone.from_hosted_zone_attributes(self, "ZoneForApp",
      hosted_zone_id=hosted_zone_id,
      zone_name=hosted_zone_name
    )

    record = route53.ARecord(self, "AliasRecord", 
      zone=zone,
      target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(cloudfront_distribution))
    )

    self._s3_bucket_name = CfnOutput(
      self, "S3BucketName",
      value=bucket.bucket_name
    )

    self._app_url = CfnOutput(
      self, "WebAppUrl",
      value="https://" + record.domain_name,
      description="The URL of the app"
    )
