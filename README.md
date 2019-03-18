# AWS-Boto3-Easy-Modules
`Deprecated`
~~AWS SDK Boto3 직접 쓰는 게 너무 복잡해서 내가 직접 쓰려고 만드는 모듈입니다.~~
[Sceptre](https://github.com/cloudreach/sceptre)와 [Troposphere](https://github.com/cloudtools/troposphere), [AWSCLI](https://aws.amazon.com/ko/cli/) 쓰세요~
Boto3 쓰다가 결국 CloudFormation으로 옮겼습니다~
```
awscli_manage_ec2.py
```

## 1. Before Using Boto3 and AWS-Boto3-Easy-Modules

### 1.1. 사용전에 알고 가야 할 내용

 - AWS SDK(Boto3)의 실행은 독립적이지 않으며, AWS CLI에 의존적입니다. 그러므로 **OS에 관계 없이**, AWS SDK(Boto3)를 사용하기 위해서는 **AWS CLI를 설치해야 합니다.**
 - AWS SDK/CLI의 **접속권한을 IAM에서 생성해야 사용 가능**합니다. 여기까지는 그렇다고 넘어갈 수 있습니다.
 - AWS SDK/CLI로 서비스를 컨트롤하는 각각의 모듈을 사용할 때, **해당 서비스에 접근할 수 있는 별도의 IAM 권한설정이 필요**합니다. 멘탈이 날아갈 수 있습니다.


### 1.2. AWS SDK(Boto3) 사용전 CLI 세팅

 - AWS CLI의 설치는 Python으로 패키징되어 배포되고 있습니다. pip로 설치 가능합니다. https://docs.aws.amazon.com/ko_kr/cli/latest/userguide/installing.html 설치를 하면 aws 명령을 사용하여 작동여부를 확인할 있습니다.
```shell
pip install awscli
aws --version
```

 - IAM이 보안과 세심한 제어를 보장하지만, 사용성을 매우 떨어뜨립니다. 일단 AWS CLI를 위한 별도의 IAM User를 생성하고, 그에 맞는 권한을 사전에 부여해야 합니다.(이 경우, EC2의 KeyPair 등은 별도로 사용하지 않아도 됩니다.) 일단 레퍼런스를 참조하겠지만 처음 보는 관점에서는 무슨 말인지 모를 수도 있을 정도로 짜증날 우려가 있습니다. https://docs.aws.amazon.com/ko_kr/cli/latest/userguide/cli-roles.html
   - 일단 AmazonEC2FullAccess 권한을 가진 IAM User를 생성합시다.
   - User를 만들 때 생성되는 AWS Access Key ID, AWS Secret Access Key 라는 것을 바로 다음에 써먹게 됩니다.
 - 설치한 AWS CLI에 IAM User를 등록해서 관리되고 있는 계정이 접근한다는 IAM 인증을 통과해야, AWS 서비스를 코드로 관리할 수 있습니다. 일단 설치한 로컬 PC에 IAM User를 등록합시다. https://docs.aws.amazon.com/ko_kr/cli/latest/userguide/cli-chap-getting-started.html
```
윈도우 : 시작키 + cmd + 엔터키
aws configure
```
   - IAM User를 만들 때 생성된 AWS Access Key ID, AWS Secret Access Key와 해당 User의 리전명, 출력형식을 입력하여 등록합니다.
   - 한번 더 aws configure를 입력하면 입력상태를 확인할 수 있습니다.
   - **aws configure --profile** 옵션을 지정하여 다중 IAM 유저 권한을 컨트롤 할 수 있습니다.(개인적인 권장)
 - 각 서비스마다 접근권한이 별도로 존재합니다. 그 때 그 때 검색하여 **서비스에 맞는 접근권한을 IAM User에 추가**해야 합니다. 진짜 피곤합니다.

## 2. Module Descriptioin
Boto3 모듈을 직접 쓰다가, EC2 관리코드 반복이 심해서 간단한 모듈로 정리하였습니다. 다른 관리형 AWS 서비스 등의 경우에도 자주 쓰는 모듈을 확장할 예정입니다.


### 2.1. class resource_ec2
 - `_getEntireListofCurrentInstances()` : 모든 EC2 인스턴스를 조회함.
 - `_createNewInstances()` : 조건에 맞게 EC2 인스턴스를 생성함.
 - `_stopInstances()` : `instancdIds`(list)에 해당하는 실행중인 EC2 인스턴스를 중지함.
 - `_startInstances()` : `instancdIds`(list)에 해당하는 중지 상태인 EC2 인스턴스를 실행함.
 - `_terminateInstances()` : `instancdIds`(list)에 해당하는 EC2 인스턴스를 제거함.

### 2.2. class client_ec2
 - `_getInfoListofFilterdInstances()` : `filterList`(list)의 필터조건에 해당하는 EC2 인스턴스의 상세 정보를 JSON으로 불러옴.
 - `_modifyInstanceType()` : 해당 `instanceId`(str)의 인스턴스 Type을 `instnaceType`(str)로 변경함.

### 2.3. client_iam
 - `_getListofInstanceProfiles()` : Boto3 세션 접속을 위해 필요한 `iamProfilename`을 조회함. `_createNewInstances()` 실행시 `iamInstanceProfile` 값이 필요함.

### 2.4. client_ssm
 - `_getSSMinfoOfInsatances()` : 간단한 EC2 인스턴스의 현황 정보를 가져옴. `_getInfoListofFilterdInstances()`의 축약판.
 - `_sendCmdToSpecificInstance()` : SSM이 설치된 EC2 인스턴스에, SSM에 Document로 사전에 등록된 작업을 원격으로 실행할 수 있음. 예를 들어, `documentName = 'AWS-RunShellScript'`의 경우, 마치 ssh 접속하여 명령을 실행하는 것처럼 리눅스 쉘명령을 원격으로 실행할 수 있음.
 - `_getListofCmdResults()` : 해당 `instanceId`의 인스턴스에 `_sendCmdToSpecificInstance()`로 전송한 명령들의 목록을 조회함.
 - `_sendCmdToCancelinprocessCmd()` : 비동기 실행되는 `_sendCmdToSpecificInstance()`의 원격명령이 아직 완료되지 않은 경우, ssh에서 ctrl+c를 하듯 실행취소 명령을 보냄.
 - `_getRusultsAfterSendCmd()` : 해당 `instanceId`에 전송한 특정 명령의 결과 메세지를 조회함. ssh에서 명령을 실행했을 경우 터미널에 표시되는 메세지들과 동일함.
