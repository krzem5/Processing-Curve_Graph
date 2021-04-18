final float MIN_X=-30;
final float MAX_X=30;
final float MIN_Y=-30;
final float MAX_Y=30;
final float POINT_COUNT=1000;


float a=0;
int tm=0;



void setup(){
	size(600,600);
	strokeCap(ROUND);
}



void draw(){
	background(255);
	stroke(130);
	strokeWeight(2);
	line(0,map(0,MIN_Y,MAX_Y,0,height),width,map(0,MIN_Y,MAX_Y,0,height));
	line(map(0,MIN_X,MAX_X,0,width),0,map(0,MIN_X,MAX_X,0,width),height);
	stroke(0);
	noFill();
	beginShape();
	tm=0;
	for (a=0;a<PI*2;a+=PI*2/POINT_COUNT){
		vertex(map(X(tm/POINT_COUNT),MIN_X,MAX_X,0,width),map(Y(tm/POINT_COUNT),MIN_Y,MAX_Y,0,height));
		tm++;
	}
	endShape();
}
