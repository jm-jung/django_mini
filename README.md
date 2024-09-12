![image](https://github.com/user-attachments/assets/5294f65f-8443-4644-a7ba-17cc98ab5a35)




<h1>테이블 설명</h1>
<h3>
  각각 User 테이블, accounts 테이블, Transaction_history 테이블을 지칭한다.</h3>
  
  
  User 테이블은, primary key인 <strong>Id</strong>가 있고 필드엔<br> 
  로그인시 사용할 이메일<br>
  비밀번호<br>
  닉네임<br>
  이름<br>
  전화번호<br>
  마지막 로그인<br>
  스태프 여부<br>
  관리자 여부<br>
  계정 활성화 여부<br>
  로 이루어져있다.
  <hr>

  accounts 테이블은, primary key인 <strong>Id</strong>가 있고,<br>
  정한 유저에 해당되는 정보를 가져와야하기 때문에 foreign key로 <strong>User_Id</strong>를 가져와야한다. 필드엔<br> 
  유저 정보<br>
  계좌번호<br>
  은행코드<br>
  계좌종류<br>
  잔액<br>
  로 이루어져있다.
  <hr>

  transactions 테이블은, primary key인 <strong>Id</strong>가 있고,<br>
  정한 계좌에 해당되는 정보를 가져와야하기 때문에 foreign key로 <strong>Accounts_Id</strong>를 가져와야한다. 필드엔<br> 
  계좌정보<br>
  거래금액<br>
  거래 후 잔액<br>
  계좌인자내역<br>
  입출금 타입<br>
  거래 타입<br>
  거래 일시<br>
  로 이루어져있다.

  
