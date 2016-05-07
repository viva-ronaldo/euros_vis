for y in `seq 1996 4 2012`;
do
  wget https://en.wikipedia.org/wiki/UEFA_Euro_${y}_Group_A
  wget https://en.wikipedia.org/wiki/UEFA_Euro_${y}_Group_B
  wget https://en.wikipedia.org/wiki/UEFA_Euro_${y}_Group_C
  wget https://en.wikipedia.org/wiki/UEFA_Euro_${y}_Group_D
done
