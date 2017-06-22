#include <algorithm>
#include <fstream>
#include <sstream>
#include <iostream> 
#include <cstdlib>
#include <sstream>
#include <cassert>
#include <vector>
#include <map>
#include <set>
#define FI(x) (x).first
#define SE(x) (x).second
#define MP(x,y) make_pair(x,y)
#define CR(x) const x&
#define trav(it, v) for(typeof((v).begin()) it = (v).begin(); it!=(v).end(); ++it)
#define rep(i,a,b) for(int i=a;i<b;++i)
#define pb push_back
#define PT(x) (cout<<x<<endl)
using namespace std;
typedef long long ll;
typedef unsigned long long ull;
typedef vector<int> vi;
typedef vector<vi> vvi;
ll pascal[512][512];
vi bb(CR(string) s) { istringstream i(s);	int x;vi rt;while(i>>x) rt.pb(x);return rt; }
ostream& operator<<(ostream& os, CR(vi) v) { os << '['; 	rep(i,0,v.size())		if(i!=v.size()-1) os << v[i] << ' ';		else os << v[i] << ']';	return os; }
void init() {rep(n,0,100) rep(k,0,n+1) if(k == n || k == 0) pascal[n][k] = 1; else pascal[n][k] = pascal[n-1][k-1]+pascal[n-1][k];}
int PC(int n, int k) { if(0 <= k && k <= n) return pascal[n][k]; else cout << "fail!" << endl; return 0;}
int ppart(int x) { return x < 0 ?  0 : x; }
vi round(vi u, int k) { vi rt(u); rep(i,0,rt.size()) if(rt[i] == k+1) rt[i] = k; return rt; }
int gcd(int a, int b) { return a < b ? gcd(b, a) : (b ? gcd(b, a%b) : a); }

// map<vi, map<vi, int> > A; A[p][u] for a permutation p and vector u is the coefficient in front of x^u in pi(p)

vi operator+(CR(vi) a, CR(vi) b) {
	vi rt(a);
	rep(i,0,rt.size()) rt[i] += b[i];
	return rt;
}

string pp(const map<vi, int>& poly, bool underscore = true) {
  if(poly.size() == 0) return "0";
	ostringstream O;
	bool first = true;
	for(map<vi, int>::const_reverse_iterator it = poly.rbegin(); it != poly.rend(); ++it) {
		if(!first) {
			if(SE(*it) >= 0) {if(SE(*it) == 1) O << " + "; else O << " + " << SE(*it)<<"*"; }
			else { if(SE(*it) == -1) O << " - "; else O << " - " << (-SE(*it))<<"*";}
		}	else {
			if(SE(*it) >= 0) {if(SE(*it) == 1) ; else O << SE(*it)<<"*"; }
			else { if(SE(*it) == -1) O << "-"; else O << "-" << (-SE(*it))<<"*";}
			first = false; }
		rep(k,0,FI(*it).size()) if(FI(*it)[k] != 0) {
			if(FI(*it)[k] == 1)	O << "x" << (k+1) << "* ";
			else O << "x" << (k+1) << "^" << (FI(*it)[k]) << "* ";
		}
		O << "1";
	}
	return O.str();
}

int compute_split(vi a, vi s) {
  vi u(a); sort(u.begin(), u.end());
  int t = 0; rep(i,0,s.size()) t += s[i];
  return u[t-1];
}

//  result,  poly
vi serve(vi a, vi s, int split=-1) { //s should be 0/1, a a range [r] for some r. will return something that is a range [r+1].
  if(split == -1) split = compute_split(a,s);
//split is the class to split. It is determined by a and s, but we provide it anyway
  int n = a.size(); vi rt(n);
  int total = 0; rep(i,0,s.size()) if(s[i]) total++;
  rep(i,0,n) if(s[i]) rt[i] = -1; else rt[i] = -2;
  int max_class = -1; rep(i,0,a.size()) if(a[i] > max_class) max_class = a[i];
  for(int K = 1; K < split; ++K) {
    rep(i,0,n) if(a[i] == K) {
      int j = i;
      while(rt[j] != -1) { ++j; j %= n; }
      rt[j] = K;
    }
  }
  for(int K = max_class; K > split; --K) {
    rep(i,0,n) if(a[i] == K) {
      int j = i;
      while(rt[j] != -2) { j += n-1; j %= n; }
      rt[j] = K + 1;
    }
  }
  rep(i,0,n) if(rt[i] == -1) rt[i] = split;
  else if(rt[i] == -2) rt[i] = split+1;
  return rt;
}

struct arrow {
  vi a, b; string w;
};

void step(vi m, int n_boxes) {
  vi a; rep(i,0,m.size()) rep(t,0,m[i]) a.push_back(i+1);
  int n = a.size();
  int split = a[n_boxes - 1];
  if(split != a[n_boxes]) cerr << "Not really splitting." << endl;
  set<vi> L, R;
  vector<arrow> log;
  do {
    L.insert(a);
    vi s(n, 1);
    rep(i,0,n-n_boxes) s[i] = 0;
    do {
      vi b = serve(a, s, split);
      R.insert(b);
      ostringstream O; {int ct = 0; rep(i,0,n) { if(s[i] == 1) { O << "x"<<(i+1); ++ct;  if(ct != n_boxes) O << "*";}}}
      arrow A; A.a = a; A.b = b; A.w = O.str();
      log.push_back(A);
      
    } while(next_permutation(s.begin(), s.end()));
  } while(next_permutation(a.begin(), a.end()));
  map<vi, int> L_rev, R_rev;
  {int k = 0; trav(it, L) L_rev[*it] = k++; }
  {int k = 0; trav(it, R) R_rev[*it] = k++; }
  vector<vector<string> > mat(L.size(), vector<string>(R.size()));
  rep(i,0,log.size()) {
    mat[L_rev[log[i].a]][R_rev[log[i].b]] = log[i].w;
  }
  cout << "Matrix([";
  rep(i,0,L.size()) {
    cout << "[";
    rep(j,0,R.size()) {
      if(mat[i][j].length() > 0)
        cout << mat[i][j];
      else
        cout << "0";
      if(j != R.size() - 1) cout << ",";
    }
    cout << "]";
    if(i != L.size() - 1) cout << "," << endl;
  }
  cout << "]);" << endl;
}

string kort(const vi& v) {
	ostringstream O;
	rep(i,0,v.size())
		O<<v[i];
	return O.str();
}

int main() {
/*
  step(bb("1 2 2"), 2);
  return 0;
*/
/*
  vi s1 = bb("0 1 0 1 0 0 0 1 0 0");
  vi s2 = bb("0 0 0 0 0 1 0 0 1 0");
  vi s3 = bb("0 0 0 1 0 0 0 1 0 0");
  vi s4 = bb("0 1 0 0 0 1 0 0 1 0");
*/
  ifstream F("tmp.txt");
  string s;
  getline(F,s); vi s1 = bb(s);
  getline(F,s); vi s2 = bb(s);
//getline(F,s);
  getline(F,s); vi s3 = bb(s);
  getline(F,s); vi s4 = bb(s);

  int n = s1.size();
  rep(t,0,(1<<n)) {
    vi p(n); rep(i,0,n) if(t & (1<<i)) p[i] = 1; else p[i] = 2;
    //cout << serve(serve(p,s1),s2) << " and " << serve(serve(p, s3), s4) << endl;
    if(serve(serve(p, s1), s2) != serve(serve(p, s3), s4)) cout << "mjau" << endl;
  }
	return 0;
}
