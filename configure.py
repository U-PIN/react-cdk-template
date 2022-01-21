import boto3
import json
import os
import sys
from argparse import ArgumentParser

loaded_params = json.load(open('config.params.json', 'r'))
cache_file = 'config.cache.json'
params = loaded_params['Parameters']
namespace = loaded_params['Namespace']
options = loaded_params['DefaultOptions']
ssm = boto3.client('ssm')
ssm_not_defined = 'not-defined'


def get_args():
  usage = 'Usage: python {} [--help]'.format(os.path.basename(__file__))
  for option in options:
    usage += ' [--{}]'.format(option['CLIFormat'])
  for param in params:
    usage += ' [--{} <value>]'.format(param['CLIFormat'])

  description = 'Use this script for configuring SSM parameters for CDK deployment.'
  argparser = ArgumentParser(usage=usage, description=description)

  for option in options:
    argparser.add_argument(
      '-' + option['ShortCLIFormat'], '--' + option['CLIFormat'],
      action=option['Action'],
      help=option['Help']
    )

  for param in params:
    argparser.add_argument(
      '--' + param['CLIFormat'],
      help=param['Description']
    )

  args = argparser.parse_args()
  return vars(args)


def is_parameters_provided(args):
  none_value_count = list(args.values()).count(None)
  return none_value_count < len(args) - len(options)


def convert_args_to_ssm_params(args):
  ssm_params = []

  for param in params:
    if args[param['CLIFormat'].replace('-', '_')] is not None:
      ssm_params.append({
        'Name': namespace + param['Name'],
        'Value': args[param['CLIFormat'].replace('-', '_')],
        'Description': param['Description'],
      })

  return ssm_params


def store_ssm_parameters(ssm_params):
  print('Storing parameters to SSM Parameter Store.')

  for ssm_param in ssm_params:
    try:
      response = ssm.put_parameter(
        Name=ssm_param['Name'],
        Value=ssm_param['Value'],
        Type='String',
        Overwrite=True,
        Description='{} under {}'.format(ssm_param['Description'], namespace)
      )
      print('The parameter "{}" has been stored in SSM Parameter Store.'.format(ssm_param['Name']))

    except Exception as e:
      print(e)


def load_ssm_parameters():
  loaded_ssm_params = []
  for param in params:
    try:
      response = ssm.get_parameter(
        Name=namespace + param['Name']
      )
      parameter = response['Parameter']
      loaded_ssm_params.append({
        'Name': parameter['Name'],
        'Value': parameter['Value'],
      })

    except ssm.exceptions.ParameterNotFound as e:
      print('Parameter "{}" has not been stored in SSM Parameter Store.'.format(param['Name']))
      loaded_ssm_params.append({
        'Name': namespace + param['Name'],
        'Value': ssm_not_defined,
      })

    except Exception as e:
      print(e)

  return loaded_ssm_params


def delete_ssm_parameters():
  print('Deleting all parameters starting with "{}" from SSM Parameter Store.'.format(namespace))
  
  try:
    response = ssm.delete_parameters(Names=[namespace + param['Name'] for param in params])
    if len(response['DeletedParameters']) == 0:
      print('No parameter stored with the namespace of "{}".'.format(namespace))
    else:
      print('Deleted parameters: {}'.format(", ".join(response['DeletedParameters'])))
  
  except Exception as e:
    print(e)


def store_parameters_to_cache(_params):
  print('Writing parameters to {} .'.format(cache_file))

  with open(cache_file, 'w') as f:
    json.dump(_params, f, ensure_ascii=False)


def load_cached_parameters():
  if os.path.exists(cache_file):
    cached_params = json.load(open(cache_file, 'r'))
    return cached_params

  else:
    return []


def get_temp_cache():
  return [{'Name': namespace + _param['Name'], 'Value': ssm_not_defined} for _param in params]


def get_cached_value(param_name, cached_params):
  return list(filter(lambda item: item['Name'] == param_name, cached_params))[0]['Value']


def get_ssm_params_interactive_mode():
  print('Please provide values for each parameters.')
  
  cached_params = load_cached_parameters()
  if len(cached_params) == 0:
    cached_params = get_temp_cache()

  ssm_params = []
  for param in params:
    prompt_str = namespace + param['Name']
    cached_val = get_cached_value(namespace + param['Name'], cached_params)
    
    if cached_val == ssm_not_defined:
      prompt_str += ': '
      
    else:
      prompt_str += ' ({}): '.format(cached_val)

    val = input(prompt_str)

    if val == '' and cached_val is not ssm_not_defined:
      val = cached_val

    if val != '' and val != ssm_not_defined:
      ssm_params.append({
        'Name': namespace + param['Name'],
        'Value': val,
        'Description': param['Description']
      })
      
  if len(ssm_params) > 0:
    return ssm_params
    
  else:
    print('At least one parameter needs to be provided if there is no cache available.')
    sys.exit()


def get_cached_params_for_test(ssm_params):
  cached_params = []

  for param in params:
    searched_param = list(filter(lambda item: item['Name'] == namespace + param['Name'], ssm_params))
    if len(searched_param) == 0:
      cached_params.append({
        'Name': namespace + param['Name'],
        'Value': ssm_not_defined,
      })
    else:
      cached_params.append({
        'Name': searched_param[0]['Name'],
        'Value': searched_param[0]['Value'],
      })
  
  return cached_params


def main():
  args = get_args()
  
  if args['delete']:
    delete_ssm_parameters()

    if os.path.exists(cache_file):
      os.remove(cache_file)
    sys.exit()

  if args['test']:
    if args['interactive']:
      test_ssm_params = get_ssm_params_interactive_mode()
      ssm_params = get_cached_params_for_test(test_ssm_params)
      store_parameters_to_cache(ssm_params)
      sys.exit()
    
    else:
      if is_parameters_provided(args):
        test_ssm_params = convert_args_to_ssm_params(args)
        ssm_params = get_cached_params_for_test(test_ssm_params)
        store_parameters_to_cache(ssm_params)
        sys.exit()

      else:
        print('At least one parameter needs to be provided for non-interactive mode.')
        sys.exit()

  if args['interactive']:
    ssm_params = get_ssm_params_interactive_mode()
    store_ssm_parameters(ssm_params)
    loaded_ssm_params = load_ssm_parameters()
    store_parameters_to_cache(loaded_ssm_params)

  else:
    if is_parameters_provided(args):
      ssm_params = convert_args_to_ssm_params(args)
      store_ssm_parameters(ssm_params)
      loaded_ssm_params = load_ssm_parameters()
      store_parameters_to_cache(loaded_ssm_params)

    else:
      print('At least one parameter needs to be provided for non-interactive mode.')

  
if __name__ == '__main__':
  main()
