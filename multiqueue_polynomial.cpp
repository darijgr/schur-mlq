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

//  result,  poly
pair<vi, vi> serve(vi a, vi s, int row_number) { //s should be 0/1, a a range [r] for some r. will return something that is a range [r+1].
	int n = a.size();assert(a.size() == s.size());
	vi rt(n);
	vi weight(n+1, 0);
	int total = 0; rep(i,0,s.size()) if(s[i]) total++;
	rep(i,0,n) if(s[i]) rt[i] = -1; else rt[i] = -2;
	set<int> T;
	int last = -1;
	rep(t,0,a.size()) T.insert(a[t]);
	trav(it, T) {
		rep(i,0,n) {
			if(a[i] == *it) {
				int j = i;
				while(rt[j] != -1) {
					if(rt[j] == -2) {
						//weight[*it]--;
						//weight[row_number]++;
						rt[j] = -3;
					}
					++j, j %= n;
				}
				rt[j] = a[i];
				--total;
			}
			if(total == 0) {
				last = *it;
				goto aut;
			} 
		}
	}
	aut:;
	rep(i,0,n) if(rt[i] <= -2) rt[i] = last+1;

  rep(i,0,s.size()) if(s[i] == 1) weight[i] = 1;
	return MP(rt, weight);
}

// map<vi, map<vi, int> > A; A[p][u] for a permutation p and vector u is the coefficient in front of x^u in pi(p)

vi operator+(CR(vi) a, CR(vi) b) {
	vi rt(a);
	rep(i,0,rt.size()) rt[i] += b[i];
	return rt;
}

string pp(const map<vi, int>& poly, bool underscore = true) {
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

void step(map<vi,map<vi,int> >& A, map<vi,map<vi, int> >& B, int k, int n, int row_number) {
	vi s(n); 
	trav(it, A) {
		vi a(FI(*it)); map<vi,int> poly(SE(*it));
		rep(t,0,1<<n) {
			s.assign(n,0);
			int ct = 0;	rep(i,0,n) if(t&(1<<i)) s[i] = 1,++ct;
			if(ct == k) {
				pair<vi, vi> pvv = serve(a,s, row_number);
				vi factor(SE(pvv));
				trav(jt, poly) { //multiply poly by SE(pvv) and add to B[FI(pvv)], SE(*jt) times
					B[FI(pvv)][FI(*jt)+factor] += SE(*jt);	
				}
				//B[serve(a,s)]+=m;
			}
		}
	}
}

map<vi, map<vi, int> > distribution(vi q) {
	map<vi, map<vi, int> > A, B;
	vi start;	rep(i,0,q.size()) rep(j,0,q[i]) start.push_back(1);
	int n = start.size();

	A[start][vi(n, 0)] = 1;
	int sum = 0;
	rep(k,0,q.size()-1) {
		cerr << k << " / " << q.size() << endl;
		sum += q[k];
		step(A, B, sum, n, k+1), swap(A,B), B.clear();
	}
	//multiply by monomial to get rid of negative powers
	vi factor(n,0);
	trav(it, A)
		trav(jt,SE(*it))
			rep(k,0,n)
				factor[k] = max(factor[k], -FI(*jt)[k]);
	trav(it, A)
		trav(jt, SE(*it))
			B[FI(*it)][FI(*jt)+factor] = SE(*jt);
	return B;
}

ll pow(ll x, int k) {
	if(!k) return 1;
	ll t = pow(x, k/2);
	return k%2 ? (t*t*x) : (t*t);
}

bool is3(int x) {return x == 1 || x == 2 || x == 3;}


bool leq(const map<vi, int>& a, const map<vi, int>& b) {
	for(map<vi,int>::const_iterator it = a.begin(); it != a.end(); ++it) {
		map<vi,int>::const_iterator jt = b.find(FI(*it));
		if(jt == b.end()) return false;
		if(*it > *jt) return false;
	}
	return true;
}

vi kod(const vi& x) {
	vi y;
	int n = x.size();
	rep(i,1,n-1) {
		int k = 0; while(x[k%n] != i) ++k;
		int l = 0;
		while(x[k%n] != i+1) {if(x[k%n]>i)++l; ++k;}
		y.push_back(l);
	}
	return y;
}

string kort(const vi& v) {
	ostringstream O;
	rep(i,0,v.size())
		O<<v[i];
	return O.str();
}

int main() {
	init();srand(time(0));string s;
	cout << "usage: enter \"1 2 3 4 4\" to get the weights of all permutations of the word 12344" << endl;
	while(getline(cin, s)) {
		vi t = bb(s);	vi q;
		for(int ty = 1;;++ty) {
			q.push_back(0);
			rep(i,0,t.size())	if(t[i] == ty) q.back()++;
			if(q.back() == 0) { q.pop_back(); break; }
		}
		map<vi, map<vi, int> > A = distribution(q);
		map<vi, int> C;
		trav(it, A) {
    if(FI(*it) == t) {
		cout << "p";
      rep(k,0,FI(*it).size())
      cout << (FI(*it))[k];
		  cout << " := " << pp(SE(*it)) <<";"<< endl;
			trav(jt, SE(*it))
			 C[FI(*jt)] += SE(*jt);
		}
    }
	}
	cout << "Z";
	return 0;
}
